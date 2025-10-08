import json
import logging
import os
import re
import time
from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from selenium.webdriver.common.by import By

from apps.fantasy.tasks.player_performance import update_complete_player_performance
from apps.kpl.models import Fixture, Gameweek
from config.settings import base
from util.selenium import SeleniumManager


logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


def extract_fixture_data_selenium(selenium_manager, match_url):
    try:
        from .fixtures import find_team

        if not selenium_manager.safe_get(match_url):
            logger.error("Failed to load match URL")
            if selenium_manager.driver:
                logger.debug(
                    f"Failed page source (first 2000 chars): {selenium_manager.driver.page_source[:2000]}"
                )
            return []

        table = selenium_manager.wait_for_elements(By.XPATH, "//*[@class='Box kiSsvW']")
        if not table:
            logger.warning("Fixture table not found on page")
            if selenium_manager.driver:
                logger.debug(
                    f"Page source when table not found (first 2000 chars): {selenium_manager.driver.page_source[:2000]}"
                )
            return []

        fixtures = table.find_elements(By.TAG_NAME, "a")
        logger.info(f"Found {len(fixtures)} fixture links")

        data = []
        for fixture_elem in fixtures:
            logger.info(f"Processing fixture element: {fixture_elem.text}")
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
        logger.error(
            f"Could not extract scores from fixture table: {e}", exc_info=True
        )
        if selenium_manager.driver:
            logger.debug(
                f"Exception page source (first 2000 chars): {selenium_manager.driver.page_source[:2000]}"
            )
        return []


def parse_scorers(text_block):
    scorers = []
    for line in text_block.splitlines():
        if not line.strip():
            continue

        # Check if this is an own goal
        is_own_goal = "(OG)" in line
        if is_own_goal:
            # Remove the (OG) marker for processing
            line = line.replace("(OG)", "").strip()

        minutes = re.findall(r"\d+'(?:\s*\+\d+)?(?:\s*\(Pen.\))?", line)

        name = line
        for m in minutes:
            name = name.replace(m, "").strip(", ").strip()

        if name:
            scorers.append(
                {
                    "name": name.strip(),
                    "minutes": [m.strip() for m in minutes],
                    "is_own_goal": is_own_goal,
                }
            )
        else:
            scorers.append(
                {"name": line.strip(), "minutes": [], "is_own_goal": is_own_goal}
            )

    return scorers


def get_goal_scorers(selenium_manager, match_link, max_retries=2):
    """
    Fetch goal scorers with retry logic
    """
    for attempt in range(max_retries):
        try:
            if not selenium_manager.safe_get(match_link):
                logger.warning(f"Failed to load match link (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return [], []

            all_section = selenium_manager.wait_for_elements(
                By.XPATH, "//*[contains(@class, 'ai_flex-start')]", timeout=10
            )

            if not all_section:
                logger.warning("Could not find scorer container section")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return [], []

            try:
                home_section = all_section.find_element(
                    By.XPATH, ".//*[contains(@class, 'ai_flex-end')]"
                )
                logger.info("Found home_section")
            except Exception as e:
                logger.warning(f"Home section not found: {e}")
                home_section = None

            try:
                away_section = all_section.find_element(
                    By.XPATH, ".//*[contains(@class, 'ai_flex-start')]"
                )
                logger.info("Found away_section")
            except Exception as e:
                logger.warning(f"Away section not found: {e}")
                away_section = None

            if not home_section or not away_section:
                logger.info("Trying independent section lookup")
                home_section = selenium_manager.wait_for_elements(
                    By.XPATH, "//*[contains(@class, 'ai_flex-end')]", timeout=5
                )
                away_section = selenium_manager.wait_for_elements(
                    By.XPATH, "//*[contains(@class, 'ai_flex-start')]", timeout=5
                )

            away_scorers = parse_scorers(away_section.text if away_section else "")
            home_scorers = parse_scorers(home_section.text if home_section else "")

            logger.info(
                f"Extracted {len(home_scorers)} home scorers and {len(away_scorers)} away scorers"
            )

            return home_scorers, away_scorers

        except Exception as e:
            logger.warning(
                f"Error getting goal scorers (attempt {attempt + 1}/{max_retries}): {e}"
            )
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return [], []

    return [], []


def update_fixture_task(selenium_manager, live_data):
    from .fixtures import find_team

    candidate_fixtures = Fixture.objects.filter(
        Q(gameweek__is_active=True) | Q(status="postponed")
    )
    matched_fixture_ids = set()

    for data in live_data:
        home_team = find_team(data["home"])
        away_team = find_team(data["away"])

        if not home_team or not away_team:
            logger.warning(f"Could not resolve teams: {data['home']} vs {data['away']}")
            continue

        matching_fixtures = [
            fixture
            for fixture in candidate_fixtures
            if fixture.home_team == home_team and fixture.away_team == away_team
        ]

        for fixture in matching_fixtures:
            matched_fixture_ids.add(fixture.id)
            logger.info(
                f"Processing fixture {fixture.home_team} vs {fixture.away_team} "
                f"(GW {fixture.gameweek.number}, status={fixture.status})"
            )

            task_name = f"monitor_fixture_{fixture.id}_{fixture.gameweek.number}"
            pt = PeriodicTask.objects.filter(name=task_name).first()

            # If fixture was postponed but now found, update its date but DO NOT enable task yet
            if fixture.status == "postponed":
                logger.info(
                    f"Fixture {fixture.id} was postponed, now updating from live data"
                )
                fixture.match_date = timezone.now()
                fixture.status = "upcoming"
                fixture.save(update_fields=["match_date", "status"])

                if pt:
                    pt.enabled = False
                    pt.save(update_fields=["enabled"])
                    logger.info(
                        f"Kept PeriodicTask disabled for fixture {fixture.id} (postponed)"
                    )

            # If match is live
            if data["is_playing"]:
                if fixture.match_date > timezone.now():
                    fixture.match_date = timezone.now()
                    fixture.save(update_fields=["match_date"])
                    logger.info(f"Adjusted match_date to now for fixture {fixture.id}")

                if fixture.status != "live":
                    fixture.status = "live"
                    fixture.save(update_fields=["status"])
                    logger.info(f"Updated fixture {fixture.id} status to live")

                if pt:
                    pt.start_time = timezone.now()
                    pt.enabled = True
                    pt.expires = timezone.now() + timedelta(hours=2)
                    pt.save(update_fields=["start_time", "enabled", "expires"])
                    logger.info(f"Enabled PeriodicTask for live fixture {fixture.id}")

            elif data["time"] == "FT":
                if fixture.status != "completed":
                    fixture.status = "completed"
                    fixture.save(update_fields=["status"])
                    logger.info(f"Updated fixture {fixture.id} status to completed")

                if pt:
                    pt.enabled = False
                    pt.expires = timezone.now()
                    pt.save(update_fields=["enabled", "expires"])
                    logger.info(
                        f"Disabled PeriodicTask for completed fixture {fixture.id}"
                    )

                # Update scores + players
                if int(data["home_score"]) > 0 or int(data["away_score"]) > 0:
                    if fixture.home_team_score != int(
                        data["home_score"]
                    ) or fixture.away_team_score != int(data["away_score"]):
                        fixture.home_team_score = int(data["home_score"])
                        fixture.away_team_score = int(data["away_score"])
                        fixture.save()

                    try:
                        home_scorers, away_scorers = get_goal_scorers(
                            selenium_manager, data["link"]
                        )
                        if home_scorers or away_scorers:
                            update_complete_player_performance(
                                fixture, home_scorers, away_scorers
                            )
                            logger.info(
                                f"Updated player performances for fixture {fixture.id} (completed)"
                            )
                    except Exception as e:
                        logger.error(
                            f"Failed to update goal scorers for fixture {fixture.id}: {e}",
                            exc_info=True
                        )

            elif data["time"].lower() == "postponed":
                if fixture.status != "postponed":
                    fixture.status = "postponed"
                    fixture.save(update_fields=["status"])
                    logger.info(f"Updated fixture {fixture.id} status to postponed")

                if pt:
                    pt.enabled = False
                    pt.save(update_fields=["enabled"])
                    logger.info(
                        f"Disabled PeriodicTask for postponed fixture {fixture.id}"
                    )

    # Handle stale fixtures
    stale_fixtures = Fixture.objects.filter(
        status__in=["completed", "postponed"]
    ).exclude(id__in=matched_fixture_ids)

    for fixture in stale_fixtures:
        task_name = f"monitor_fixture_{fixture.id}_{fixture.gameweek.number if fixture.gameweek else 'N/A'}"
        pt = PeriodicTask.objects.filter(name=task_name, enabled=True).first()
        if pt:
            pt.enabled = False
            pt.expires = timezone.now()
            pt.save(update_fields=["enabled", "expires"])
            logger.info(
                f"Disabled PeriodicTask for stale fixture {fixture.id} ({fixture.status})"
            )


@shared_task
def monitor_fixture_score(fixture_id=None):
    selenium_manager = None
    successful_updates = 0
    failed_updates = 0
    
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
            fixtures = Fixture.objects.exclude(status="completed")

        if len(fixtures) < 1:
            logger.info("No fixtures found")
            return False

        match_url = os.getenv("MATCHES_URL")
        if not match_url:
            logger.error("MATCHES_URL not set in environment")
            return False

        try:
            selenium_manager = SeleniumManager(timeout=30)
            driver = selenium_manager.get_driver()
            if not driver:
                logger.error("Failed to initialize Selenium driver")
                return False

            live_data = extract_fixture_data_selenium(selenium_manager, match_url)

            if not live_data:
                logger.warning("No live data extracted from main page")
                return False

        except Exception as e:
            logger.error(f"Failed to extract fixture data: {e}", exc_info=True)
            if selenium_manager:
                try:
                    selenium_manager.close()
                except:
                    pass
            return False

        try:
            update_fixture_task(selenium_manager, live_data)
        except Exception as e:
            logger.error(f"Error updating fixture tasks: {e}", exc_info=True)

        updates = 0
        goals_updated = 0

        # Process fixtures without recreating selenium manager
        for fixture in fixtures:
            try:
                fixture_updated = False

                for data in live_data:
                    home_team = find_team(data["home"])
                    away_team = find_team(data["away"])

                    if not (
                        fixture.home_team == home_team
                        and fixture.away_team == away_team
                    ):
                        continue

                    old_home_score = fixture.home_team_score
                    old_away_score = fixture.away_team_score

                    if fixture.home_team_score != int(
                        data["home_score"]
                    ) or fixture.away_team_score != int(data["away_score"]):

                        fixture.home_team_score = int(data["home_score"])
                        fixture.away_team_score = int(data["away_score"])
                        updates += 1
                        fixture_updated = True

                        logger.info(
                            f"Score update: {fixture.home_team.name} {old_home_score}->{fixture.home_team_score}, "
                            f"{fixture.away_team.name} {old_away_score}->{fixture.away_team_score}"
                        )

                    if data["is_playing"]:
                        if fixture.status != "live":
                            fixture.status = "live"
                            fixture_updated = True

                        try:
                            time.sleep(2)  # Brief delay before fetching scorers

                            home_scorers, away_scorers = get_goal_scorers(
                                selenium_manager, data["link"]
                            )

                            if home_scorers or away_scorers:
                                update_complete_player_performance(
                                    fixture, home_scorers, away_scorers
                                )
                                goals_updated += 1
                                successful_updates += 1
                                logger.info(
                                    f"Updated player performances for fixture {fixture.id} "
                                    f"(status: {fixture.status})"
                                )
                            else:
                                logger.warning(
                                    f"No scorers found for fixture {fixture.id}"
                                )
                        except Exception as e:
                            failed_updates += 1
                            logger.error(
                                f"Failed to update goal scorers for fixture {fixture.id}: {e}",
                                exc_info=True
                            )

                    if fixture_updated:
                        fixture.save()

                    break

                disable_fixture(fixture)

            except Exception as e:
                failed_updates += 1
                logger.error(
                    f"Error processing fixture {fixture.id}: {e}", exc_info=True
                )
                continue

        logger.info(
            f"Fixture monitoring completed: {updates} score updates, "
            f"{goals_updated} goal data updates, "
            f"{successful_updates} successful, {failed_updates} failed"
        )
        
        # Return True only if we had some success or no fixtures to process
        return failed_updates == 0 or successful_updates > 0

    except Exception as e:
        logger.error(f"Error monitoring fixtures: {e}", exc_info=True)
        return False

    finally:
        if selenium_manager:
            try:
                selenium_manager.close()
                logger.info("Selenium manager closed successfully")
            except Exception as e:
                logger.error(f"Error closing selenium manager: {e}")


@shared_task
def setup_gameweek_monitoring():
    try:
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        if not active_gameweek:
            logger.info("No active gameweek")
            return False

        fixtures = Fixture.objects.filter(gameweek=active_gameweek).order_by(
            "match_date"
        )

        if not fixtures.exists():
            logger.info("No fixtures found for active gameweek")
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
            task_name = f"monitor_fixture_{fixture.id}_{active_gameweek.number}"

            existing_task = PeriodicTask.objects.filter(name=task_name).first()

            if existing_task:
                existing_task.enabled = True
                existing_task.start_time = start_time
                existing_task.expires = end_time
                existing_task.save(update_fields=["enabled", "start_time", "expires"])
                tasks_updated += 1
                logger.info(f"Updated monitoring task for fixture {fixture.id}")
            else:
                PeriodicTask.objects.create(
                    interval=schedule,
                    name=task_name,
                    task="apps.kpl.tasks.live_games.monitor_fixture_score",
                    args=json.dumps([]),
                    kwargs=json.dumps({"fixture_id": str(fixture.id)}),
                    start_time=start_time,
                    expires=end_time,
                    enabled=True,
                )
                tasks_created += 1
                logger.info(f"Created monitoring task for fixture {fixture.id}")

        logger.info(
            f"Created {tasks_created} new tasks, updated {tasks_updated} tasks for gameweek {active_gameweek.number}"
        )
        return f"Set up {tasks_created + tasks_updated} monitoring tasks for gameweek {active_gameweek.number}"

    except Exception as e:
        logger.error(f"Error setting up gameweek monitoring: {e}", exc_info=True)
        return f"Error setting up gameweek monitoring: {e}"


def disable_fixture(fixture):
    """Disable monitoring task for completed fixtures"""
    if fixture.status == "completed":
        task_name = f"monitor_fixture_{fixture.id}_{fixture.gameweek.number}"
        try:
            periodic_task = PeriodicTask.objects.get(name=task_name)
            if periodic_task.enabled:
                periodic_task.enabled = False
                periodic_task.expires = timezone.now()
                periodic_task.save(update_fields=["enabled", "expires"])
                logger.info(f"Disabled monitoring task for completed fixture {fixture.id}")
        except PeriodicTask.DoesNotExist:
            logger.debug(f"Periodic task {task_name} not found (already deleted or never created)")
        except Exception as e:
            logger.error(f"Error disabling task {task_name}: {e}", exc_info=True)