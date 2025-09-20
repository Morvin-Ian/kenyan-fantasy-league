import logging
import os
import re
from datetime import timedelta

from celery import shared_task
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
import json

from selenium.webdriver.common.by import By

from apps.kpl.models import Fixture, Gameweek, Player
from apps.fantasy.models import PlayerPerformance
from config.settings import base
from util.selenium import SeleniumManager  

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


def extract_fixture_data_selenium(selenium_manager, match_url):
    try:
        from .fixtures import find_team  
        
        if not selenium_manager.safe_get(match_url):
            logger.error("Failed to load match URL")
            return []
            
        table = selenium_manager.wait_for_elements(By.XPATH, "//*[@class='Box kiSsvW']")
        if not table:
            logger.warning("Fixture table not found on page")
            if selenium_manager.driver:
                logger.debug(selenium_manager.driver.page_source[:2000])  
            return []

        fixtures = table.find_elements(By.TAG_NAME, "a")
        logger.info(f"Found {len(fixtures)} fixture links")

        data = []
        for fixture_elem in fixtures:
            link = fixture_elem.get_attribute("href")
            parts = fixture_elem.text.strip().splitlines()
            logger.info(f"Raw fixture parts: {parts}")

            if len(parts) >= 4:
                if len(parts) >= 6:
                    date, time, home, away, home_score, away_score = parts[:6]
                    is_playing = True
                    if time == "FT":
                        is_playing = False
                else:
                    date, time, home, away = parts[:4]
                    home_score, away_score = "0", "0"
                    is_playing = False
                    
                home_team = find_team(home)
                away_team = find_team(away)

                if not home_team or not away_team:
                    logger.warning(f"Could not resolve teams: {home} vs {away}")
                else:
                    logger.info(f"Resolved teams: {home_team.name} vs {away_team.name}")
                    
                fixture_data = {
                    "date": date,
                    "time": time,
                    "home": home,
                    "away": away,
                    "home_score": home_score,
                    "away_score": away_score,
                    "link": link,
                    "is_playing": is_playing,
                }
                logger.info(f"Fixture Data: {fixture_data}")
                data.append(fixture_data)
            else:
                logger.warning(f"Unexpected fixture format: {parts}")
        return data

    except Exception as e:
        logger.warning(f"Could not extract scores from fixture table: {e}", exc_info=True)
        return []
    
    
    
def parse_scorers(text_block):
    scorers = []
    for line in text_block.splitlines():
        if not line.strip():
            continue
        
        minutes = re.findall(r"\d+'(?:\s*\+\d+)?(?:\s*\(Pen.\))?", line)
        
        name = line
        for m in minutes:
            name = name.replace(m, "").strip(", ").strip()
        
        if name:
            scorers.append({
                "name": name.strip(),
                "minutes": [m.strip() for m in minutes]
            })
        else:
            scorers.append({"name": line.strip(), "minutes": []})
    
    return scorers


def get_goal_scorers(selenium_manager, match_link):
    if not selenium_manager.safe_get(match_link):
        logger.error("Failed to load match link")
        return [], []
        
    all_section = selenium_manager.wait_for_elements(By.XPATH, "//*[contains(@class, 'ai_flex-start')]")
    
    if not all_section:
        logger.warning("Could not find scorer container section")
    
    if not all_section:
        logger.error("No scorer sections found at all")
        return [], []
    
    try:
        home_section = all_section.find_element(By.XPATH, ".//*[contains(@class, 'ai_flex-end')]")
    except Exception as e:
        logger.warning(f"Home section not found: {e}")
        home_section = None
    
    try:
        away_section = all_section.find_element(By.XPATH, ".//*[contains(@class, 'ai_flex-start')]")
    except Exception as e:
        logger.warning(f"Away section not found: {e}")
        away_section = None
    
    if not home_section or not away_section:
        logger.info("Trying independent section lookup")
        home_section = selenium_manager.wait_for_elements(By.XPATH, "//*[contains(@class, 'ai_flex-end')]")
        away_section = selenium_manager.wait_for_elements(By.XPATH, "//*[contains(@class, 'ai_flex-start')]")
    
    
    away_scorers = parse_scorers(away_section.text if away_section else "")
    home_scorers = parse_scorers(home_section.text if home_section else "")

    logger.info(f"Extracted {len(home_scorers)} home scorers and {len(away_scorers)} away scorers")
    
    return home_scorers, away_scorers



def update_fixture_task(live_data, fixtures):
    from .fixtures import find_team
    
    for data in live_data:
        if data['is_playing']:
            home_team = find_team(data["home"])
            away_team = find_team(data["away"])
            
            matching_fixtures = [
                fixture for fixture in fixtures 
                if fixture.home_team == home_team and fixture.away_team == away_team
            ]
            
            for fixture in matching_fixtures:
                logger.info(fixture.home_team)
                if fixture.match_date > timezone.now():
                    fixture.match_date = timezone.now()
                    fixture.save(update_fields=["match_date"])
                    logger.info(f"Adjusted match_date to now for fixture {fixture.id}")
                
                task_name = f"monitor_fixture_{fixture.id}_{fixture.gameweek.number}"
                pt = PeriodicTask.objects.filter(name=task_name).first()
                
                if pt:
                    if pt.start_time > timezone.now():
                        pt.start_time = timezone.now()
                    pt.enabled = True
                    pt.expires = pt.start_time + timedelta(hours=2)
                    pt.save(update_fields=["start_time", "enabled"])
                    logger.info(f"Updated PeriodicTask start/end time for fixture {fixture.id}")
                    

def update_player_performance(fixture, home_scorers, away_scorers):
    from .fixtures import find_player
    
    for player_data in home_scorers:
        name = player_data["name"]
        goal_minutes = player_data["minutes"]
        num_goals = len(goal_minutes)
        
        player_obj = find_player(name)
        
        if not player_obj:
            player_obj = Player.objects.create(
                name=name,
                team=fixture.home_team,
                position="FWD",
                current_value=6.00
            )
            logger.info(f"Created new player: {name} for team {fixture.home_team.name}")
        
        if player_obj.team != fixture.home_team:
            player_obj.team = fixture.home_team
            player_obj.save()
        
        gameweek = fixture.gameweek
        performance, created = PlayerPerformance.objects.get_or_create(
            player=player_obj,
            gameweek=gameweek
        )
        
        if created or performance.goals_scored < num_goals:
            performance.goals_scored = num_goals
            performance.fantasy_points = max(performance.fantasy_points, num_goals * 4)
            performance.minutes_played = 90  
            performance.save()
            logger.info(f"Updated performance for {name}: {num_goals} goals in GW{gameweek.number}")

    for player_data in away_scorers:
        name = player_data["name"]
        goal_minutes = player_data["minutes"]
        num_goals = len(goal_minutes)
        
        player_obj = find_player(name)
        
        if not player_obj:
            player_obj = Player.objects.create(
                name=name,
                team=fixture.away_team,
                position="Unknown",
                current_value=4.00
            )
            logger.info(f"Created new player: {name} for team {fixture.away_team.name}")
        
        if player_obj.team != fixture.away_team:
            player_obj.team = fixture.away_team
            player_obj.save()
        
        gameweek = fixture.gameweek
        performance, created = PlayerPerformance.objects.get_or_create(
            player=player_obj,
            gameweek=gameweek
        )
        
        if created or performance.goals_scored < num_goals:
            performance.goals_scored = num_goals
            performance.fantasy_points = max(performance.fantasy_points, num_goals * 4)
            performance.minutes_played = 90  
            performance.save()
            logger.info(f"Updated performance for {name}: {num_goals} goals in GW{gameweek.number}")
        
                    
@shared_task
def monitor_fixture_score(fixture_id=None):
    selenium_manager = None
    try:
        from .fixtures import find_team
        
        if fixture_id:
            try:
                fixture = Fixture.objects.get(id=fixture_id)
                fixtures = [fixture]
            except Fixture.DoesNotExist:
                logger.error(f"Fixture {fixture_id} not found")
                return False
        else:
            fixtures = Fixture.objects.exclude(status='completed')
        
        if len(fixtures) < 1:
            logger.info("No fixtures found")
            return False
        
        logger.info(f"Monitoring {len(fixtures)} fixtures")
        match_url = os.getenv("MATCHES_URL")
        if not match_url:
            logger.error("MATCHES_URL not set in environment")
            return False
        
        try:
            selenium_manager = SeleniumManager(max_retries=3, retry_delay=2)
            driver = selenium_manager.get_driver()
            if not driver:
                logger.error("Failed to initialize Selenium driver")
                return False
            
            live_data = extract_fixture_data_selenium(selenium_manager, match_url)
            if not live_data:
                logger.warning("No live data extracted from website")
                return False
            
            updates = 0
            goals_updated = 0
            
            update_fixture_task(live_data, fixtures)
            
            for fixture in fixtures:
                
                for data in live_data:
                    home_team = find_team(data["home"])
                    away_team = find_team(data["away"])
                    
                    if data['time'] == "FT":
                        fixture.status = 'completed'
                    elif data['is_playing']:
                        fixture.status = 'live'
                    
                    if (fixture.home_team == home_team and 
                        fixture.away_team == away_team and 
                        data["is_playing"]):
                        
                        if (fixture.home_team_score != int(data['home_score']) or 
                            fixture.away_team_score != int(data['away_score'])):
                            
                            fixture.home_team_score = int(data['home_score'])
                            fixture.away_team_score = int(data['away_score'])
                            updates += 1
                        
                        # Update goal scorers
                        home_scorers, away_scorers = get_goal_scorers(selenium_manager, data["link"])
                        update_player_performance(fixture, home_scorers, away_scorers)
                        
                        goals_updated += 1
                
                fixture.save()
                disable_fixture(fixture)
            
            logger.info(f"Fixture monitoring completed: {updates} score updates, {goals_updated} goal data updates")
            return True
        finally:
            if selenium_manager:
                selenium_manager.close()
    
    except Exception as e:
        logger.error(f"Error monitoring fixtures: {e}")
        return False
    
    
    
    
@shared_task
def setup_gameweek_monitoring():
    try:
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        if not active_gameweek:
            logger.info("No active gameweek")
            return False
        
        fixtures = Fixture.objects.filter(gameweek=active_gameweek).order_by('match_date')
        
        if not fixtures.exists():
            return "No fixtures found for active gameweek"
        
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=5,
            period=IntervalSchedule.MINUTES,
        )
        
        tasks_created = 0
        tasks_updated = 0
        
        
        for fixture in fixtures:
            start_time = fixture.match_date - timedelta(minutes=30)            
            end_time = fixture.match_date + timedelta(hours=2)
            task_name = f'monitor_fixture_{fixture.id}_{active_gameweek.number}'
            
            existing_task = PeriodicTask.objects.filter(name=task_name).first()
            
            if existing_task:
                existing_task.enabled = True
                existing_task.save()
                logger.info(f"Updated monitoring task for fixture {fixture.id}")
            else:
                task = PeriodicTask.objects.create(
                    interval=schedule,
                    name=task_name,
                    task='apps.kpl.tasks.live_games.monitor_fixture_score',
                    args=json.dumps([]),
                    kwargs=json.dumps({'fixture_id': str(fixture.id)}),  
                    start_time=start_time,
                    expires=end_time,
                    enabled=True,
                )
        
        logger.info(f"Created {tasks_created} new tasks, updated {tasks_updated} tasks for gameweek {active_gameweek.number}")
        return f"Set up {tasks_created + tasks_updated} monitoring tasks for gameweek {active_gameweek.number}"
        
    except Exception as e:
        logger.error(f"Error setting up gameweek monitoring: {e}")
        return f"Error setting up gameweek monitoring: {e}"

def disable_fixture(fixture):
    if fixture.status == 'completed':
        task_name = f"monitor_fixture_{fixture.id}_{fixture.gameweek.number}"
        try:
            periodic_task = PeriodicTask.objects.get(name=task_name)
            periodic_task.enabled = False
            periodic_task.save(update_fields=["enabled"])
            logger.info(f"Disabled monitoring task for completed fixture {fixture.id}")
        except PeriodicTask.DoesNotExist:
            logger.warning(f"Periodic task {task_name} not found for disabling")
        except Exception as e:
            logger.error(f"Error disabling task {task_name}: {e}")