import logging
import os
import re
from datetime import timedelta
from uuid import UUID

from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from apps.kpl.models import Fixture, Gameweek
from config.settings import base

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)



def wait_for_elements(driver, by, element_identifier, timeout=15):
    try:
        WebDriverWait(driver, timeout).until(
            ec.visibility_of_element_located((by, element_identifier))
        )
        logger.info(f"{element_identifier} found and loaded")
        return driver.find_element(by, element_identifier)
    except TimeoutException:
        logger.error(f"Timeout waiting for {element_identifier}")
        return None



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



def get_selenium_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    
    try:
        driver = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=options
        )
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        logger.info("Using remote Selenium driver")
        return driver
    except Exception as e:
        logger.warning(f"Remote driver failed: {e}")
        return None


def extract_fixture_data_selenium(driver, match_url):
    try:
        from .fixtures import find_team  # import inside to avoid circular imports
        driver.get(match_url)        
        table = wait_for_elements(driver, By.XPATH, "//*[@class='Box kiSsvW']")
        if not table:
            logger.warning("Fixture table not found on page")
            logger.debug(driver.page_source[:2000])  # dump some HTML for inspection
            return []

        fixtures = table.find_elements(By.TAG_NAME, "a")
        logger.info(f"Found {len(fixtures)} fixture links")

        data = []
        for fixture_elem in fixtures:
            link = fixture_elem.get_attribute("href")
            parts = fixture_elem.text.strip().splitlines()
            logger.debug(f"Raw fixture parts: {parts}")

            if len(parts) >= 4:
                if len(parts) >= 6:
                    date, time, home, away, home_score, away_score = parts[:6]
                    is_playing = True
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



def get_goal_scorers(driver, match_link):
    driver.get(match_link)
    
    all_section = wait_for_elements(driver, By.XPATH, "//*[contains(@class, 'ai_flex-start')]")
    home_section = all_section.find_element(By.XPATH, ".//*[contains(@class, 'ai_flex-end')]")
    away_section = all_section.find_element(By.XPATH, ".//*[contains(@class, 'ai_flex-start')]")
    
    away_scorers = parse_scorers(away_section.text if away_section else "")
    home_scorers = parse_scorers(home_section.text if home_section else "")

    logger.info(f"Extracted scorers - Home: {home_scorers}, Away: {away_scorers}")
    return home_scorers, away_scorers


@shared_task
def monitor_fixture_score(fixture_id=None):
    try:
        from .fixtures import find_team
        
        # If fixture_id is provided, monitor only that fixture
        if fixture_id:
            try:
                fixture = Fixture.objects.get(id=fixture_id)
                fixtures = [fixture]
            except Fixture.DoesNotExist:
                logger.error(f"Fixture {fixture_id} not found")
                return f"Fixture {fixture_id} not found"
        else:
            # Fallback: monitor all fixtures in active gameweek
            active_gameweek = Gameweek.objects.filter(is_active=True).first()
            if not active_gameweek:
                logger.info("No active gameweek found for monitoring")
                return "No active gameweek found"
            
            fixtures = Fixture.objects.filter(
                gameweek=active_gameweek,
                status__in=['upcoming', 'live']
            )
        
        if len(fixtures) < 1:
            logger.info("No fixtures found for monitoring")
            return "No fixtures found"
        
        logger.info(f"Monitoring {len(fixtures)} fixtures")
        
        match_url = os.getenv("MATCHES_URL")
        if not match_url:
            logger.error("MATCHES_URL not set in environment")
            return "MATCHES_URL not configured"
        
        driver = None
        try:
            driver = get_selenium_driver()
            if not driver:
                logger.error("Failed to initialize Selenium driver")
                return "Selenium driver initialization failed"
            
            # Scrape all fixture data once
            live_data = extract_fixture_data_selenium(driver, match_url)
            
            if not live_data:
                logger.warning("No live data extracted from website")
                return "No live data extracted"
            
            updates = 0
            goals_updated = 0
            
            # Process each fixture against the scraped data
            for fixture in fixtures:
                fixture_updated = False
                
                for data in live_data:
                    # Find matching fixture in scraped data
                    home_team = find_team(data["home"])
                    away_team = find_team(data["away"])
                    
                    if (fixture.home_team == home_team and 
                        fixture.away_team == away_team) and data['is_playing']:
                        
                        # Update scores if they changed
                        if (fixture.home_team_score != int(data['home_score']) or 
                            fixture.away_team_score != int(data['away_score'])):
                            
                            fixture.home_team_score = int(data['home_score'])
                            fixture.away_team_score = int(data['away_score'])
                            
                            # Update status based on scores and time
                            if data['is_playing']:
                                fixture.status = 'live'
                            elif data['time'] == 'FT':
                                fixture.status = 'completed'
                            
                            fixture_updated = True
                            updates += 1
                            logger.info(f"Updated scores: {fixture.home_team} {data['home_score']}-{data['away_score']} {fixture.away_team}")
                        
                        # Get goal scorers for live/playing matches
                        if data['is_playing']:
                            try:
                                home_scorers, away_scorers = get_goal_scorers(driver, data["link"])
                                # Update goal scorers in your database
                                goals_updated += 1
                                logger.info(f"Extracted scorers for {fixture.home_team} vs {fixture.away_team}")
                            except Exception as e:
                                logger.warning(f"Could not extract scorers for {fixture}: {e}")
                        
                        break
                
                if fixture_updated:
                    fixture.save()
            
            logger.info(f"Fixture monitoring completed: {updates} score updates, {goals_updated} goal data updates")
            return f"Updated {updates} fixtures, processed {goals_updated} goal records"
            
        finally:
            if driver:
                driver.quit()
            logger.info("Selenium driver closed")
                
    except Exception as e:
        logger.error(f"Error monitoring fixtures: {e}")
        return f"Error monitoring fixtures: {e}"

@shared_task
def setup_gameweek_monitoring():
    try:
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        if not active_gameweek:
            return "No active gameweek found"
        
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
            # TEST MODE: Start 5 minutes from now, run for 10 minutes
            start_time = timezone.now() + timedelta(minutes=1)
            end_time = start_time + timedelta(minutes=10)
            
            task_name = f'monitor_fixture_{fixture.id}_{active_gameweek.number}'
            
            existing_task = PeriodicTask.objects.filter(name=task_name).first()
            
            if existing_task:
                # Update existing task with test timing
                existing_task.interval = schedule
                # existing_task.start_time = start_time
                # existing_task.expires = end_time
                existing_task.enabled = True
                existing_task.save()
                tasks_updated += 1
                logger.info(f"Updated TEST monitoring task for fixture {fixture.id} (starts: {start_time}, ends: {end_time})")
            else:
                # Create new test task for this specific fixture
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
                tasks_created += 1
                logger.info(f"Created TEST monitoring task for fixture {fixture.id} (starts: {start_time}, ends: {end_time})")
        
        logger.info(f"Created {tasks_created} new TEST tasks, updated {tasks_updated} TEST tasks for gameweek {active_gameweek.number}")
        return f"Set up {tasks_created + tasks_updated} TEST monitoring tasks starting in 5 mins for 10 mins duration"
        
    except Exception as e:
        logger.error(f"Error setting up test gameweek monitoring: {e}")
        return f"Error setting up test gameweek monitoring: {e}"
    
# @shared_task
# def setup_gameweek_monitoring():
#     try:
#         active_gameweek = Gameweek.objects.filter(is_active=True).first()
#         if not active_gameweek:
#             return "No active gameweek found"
        
#         fixtures = Fixture.objects.filter(gameweek=active_gameweek).order_by('match_date')
        
#         if not len(fixtures) < 1:
#             return "No fixtures found for active gameweek"
        
#         # Create 5-minute interval schedule
#         schedule, created = IntervalSchedule.objects.get_or_create(
#             every=5,
#             period=IntervalSchedule.MINUTES,
#         )
        
#         tasks_created = 0
#         tasks_updated = 0
        
#         for fixture in fixtures:
#             # Calculate start time (fixture start time minus buffer)
#             start_time = fixture.match_date - timedelta(minutes=30)
            
#             # Calculate end time (fixture end time plus buffer)
#             end_time = fixture.match_date + timedelta(hours=2)
            
#             task_name = f'monitor_fixture_{fixture.id}_{active_gameweek.number}'
            
#             existing_task = PeriodicTask.objects.filter(name=task_name).first()
            
#             if existing_task:
#                 # Update existing task with new timing
#                 existing_task.interval = schedule
#                 existing_task.start_time = start_time
#                 existing_task.expires = end_time
#                 existing_task.enabled = True
#                 existing_task.save()
#                 tasks_updated += 1
#                 logger.info(f"Updated monitoring task for fixture {fixture.id}")
#             else:
#                 # Create new task for this specific fixture
#                 task = PeriodicTask.objects.create(
#                     interval=schedule,
#                     name=task_name,
#                     task='apps.kpl.tasks.live_games.monitor_fixture_score',
#                     args=json.dumps([]),
#                     kwargs=json.dumps({'fixture_id': str(fixture.id)}),  
#                     start_time=start_time,
#                     expires=end_time,
#                     enabled=True,
#                 )
#                 tasks_created += 1
#                 logger.info(f"Created monitoring task for fixture {fixture.id}")
        
#         logger.info(f"Created {tasks_created} new tasks, updated {tasks_updated} tasks for gameweek {active_gameweek.number}")
#         return f"Set up {tasks_created + tasks_updated} monitoring tasks for gameweek {active_gameweek.number}"
        
#     except Exception as e:
#         logger.error(f"Error setting up gameweek monitoring: {e}")
#         return f"Error setting up gameweek monitoring: {e}"


def disable_fixture_monitoring_tasks(gameweek_number):
    """
    Disable all individual fixture monitoring tasks for a gameweek
    """
    try:
        fixtures = Fixture.objects.filter(gameweek__number=gameweek_number)
        for fixture in fixtures:
            disable_fixture_monitoring_task(fixture.id)
        logger.info(f"Disabled individual monitoring tasks for gameweek {gameweek_number}")
    except Exception as e:
        logger.error(f"Error disabling fixture tasks for gameweek {gameweek_number}: {e}")


def disable_fixture_monitoring_task(fixture_id: UUID):
    try:
        task_name = f'monitor_fixture_{str(fixture_id)}'
        task = PeriodicTask.objects.filter(name=task_name).first()
        if task:
            task.enabled = False
            task.save()
            logger.info(f"Disabled monitoring task for fixture {fixture_id}")
    except Exception as e:
        logger.error(f"Error disabling monitoring task for fixture {fixture_id}: {e}")
