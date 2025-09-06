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
def monitor_fixture_score(fixture_id: str):
    try:
        from .fixtures import find_team

        fixture_uuid = UUID(fixture_id)
        fixture = Fixture.objects.get(id=fixture_uuid)
        
        logger.info(f"Monitoring fixture: {fixture.home_team} vs {fixture.away_team}")
        
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
            
            live_data = extract_fixture_data_selenium(driver, "https://www.sofascore.com/tournament/football/kenya/premier-league/1644#id:45686,tab:matches")
            
            if not live_data:
                logger.warning(f"No live data extracted for fixture {fixture_id}")
                return f"No live data for fixture {fixture_id}"

            for data in live_data:            
                if data['is_playing']:
                    home_scorers, away_scorers = get_goal_scorers(driver, data["link"])
                    if 'home_score' in data and 'away_score' in data:
                        if fixture.home_team == find_team(data["home"]) and fixture.away_team == find_team(data["away"]) and fixture.gameweek.is_active:
                            if (fixture.home_team_score != data['home_score'] or 
                                fixture.away_team_score != data['away_score']):
                                
                                fixture.home_team_score = data['home_score']
                                fixture.away_team_score = data['away_score']
                                logger.info(f"Updated scores: {fixture.home_team} {data['home_score']} - {data['away_score']} {fixture.away_team}")
                    logger.info("Scorers:", away_scorers)
                    
            
            return f"Monitored fixture {fixture_id}"
            
        finally:
            if driver:
                driver.quit()
            logger.info("Closing Selenium driver")
                
    except Fixture.DoesNotExist:
        logger.error(f"Fixture {fixture_id} not found")
        return f"Fixture {fixture_id} not found"
    except Exception as e:
        logger.error(f"Error monitoring fixture {fixture_id}: {e}")
        return f"Error monitoring fixture {fixture_id}: {e}"


def create_fixture_monitoring_task(fixture_id: UUID):
    try:        
        fixture = Fixture.objects.get(id=fixture_id)
        logger.info(f"Fixture found: {fixture.home_team} vs {fixture.away_team}, Status: {fixture.status}")
        
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=2,
            period=IntervalSchedule.MINUTES,
        )
        
        task_name = f'monitor_fixture_{str(fixture_id)}'
        existing_task = PeriodicTask.objects.filter(name=task_name).first()
        
        if existing_task:
            existing_task.enabled = True
            existing_task.save()
            logger.info(f"Enabled existing monitoring task for fixture {fixture_id}: {task_name}")
        else:
            task = PeriodicTask.objects.create(
                interval=schedule,
                name=task_name,
                task='apps.kpl.tasks.live_games.monitor_fixture_score',
                args=json.dumps([str(fixture_id)]),
                enabled=True,
            )
            logger.info(f"Created new monitoring task for fixture {fixture_id}: {task_name}, Task ID: {task.id}")
            
    except Fixture.DoesNotExist:
        logger.error(f"Fixture {fixture_id} does not exist")
    except Exception as e:
        logger.error(f"Error creating monitoring task for fixture {fixture_id}: {e}", exc_info=True)



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


@shared_task
def setup_gameweek_monitoring():
    try:
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        if not active_gameweek:
            return "No active gameweek found"
        
        upcoming_fixtures = Fixture.objects.filter(
            gameweek=active_gameweek,
            status__in=['upcoming', 'live']
        )
        
        tasks_created = 0
        for fixture in upcoming_fixtures:
            create_fixture_monitoring_task(fixture.id)
            tasks_created += 1
        
        logger.info(f"Set up monitoring for {tasks_created} fixtures in Gameweek {active_gameweek.number}")
        return f"Set up monitoring for {tasks_created} fixtures in Gameweek {active_gameweek.number}"
        
    except Exception as e:
        logger.error(f"Error setting up gameweek monitoring: {e}")
        return f"Error setting up gameweek monitoring: {e}"
