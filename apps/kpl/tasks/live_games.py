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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from apps.kpl.services.match_events import MatchEventService
from apps.kpl.tasks.gameweeks import setup_team_finalization_task
from apps.kpl.models import Fixture, Gameweek
from config.settings import base
from util.selenium import SeleniumManager


logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


def extract_fixture_data(selenium_manager, match_url):
    try:
        if not selenium_manager.safe_get(match_url):
            logger.error("Failed to load match URL")
            return []

        WebDriverWait(selenium_manager.driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info("Page loaded, waiting for dynamic content...")
        time.sleep(20)

        league_containers = selenium_manager.driver.find_elements(
            By.CSS_SELECTOR, ".flex.flex-col.border.rounded-xl"
        )

        if not league_containers:
            logger.warning("No league containers found on page")
            return []

        logger.info(f"Found {len(league_containers)} league containers")

        all_matches_data = []

        for container in league_containers:
            try:
                league_elem = container.find_element(
                    By.CSS_SELECTOR, ".font-semibold.text-sm.bg-black-lighter"
                )
                league_name = league_elem.text.strip()
                logger.info(f"Processing league: {league_name}")

                matches = container.find_elements(By.CSS_SELECTOR, ".m-1.border-b")
                logger.info(f"Found {len(matches)} matches in {league_name}")

                for match in matches:
                    fixture_data = {
                        "league": league_name,
                        "home": "",
                        "away": "",
                        "home_score": "0",
                        "away_score": "0",
                        "time": "",
                        "is_playing": False,
                        "link": "",
                    }

                    teams = match.find_elements(By.CSS_SELECTOR, ".col-span-5")
                    if len(teams) >= 2:
                        home_team_div = teams[0].find_element(
                            By.CSS_SELECTOR, "div:last-child"
                        )
                        fixture_data["home"] = home_team_div.text.strip()
                        away_team_div = teams[1].find_element(
                            By.CSS_SELECTOR, "div:last-child"
                        )
                        fixture_data["away"] = away_team_div.text.strip()

                    middle_col = match.find_element(By.CSS_SELECTOR, ".col-span-2")
                    try:
                        score_container = middle_col.find_element(
                            By.CSS_SELECTOR, ".flex.flex-col.items-center"
                        )
                        score_div = score_container.find_element(
                            By.CSS_SELECTOR, ".flex"
                        )
                        score_elements = score_div.find_elements(By.TAG_NAME, "div")

                        if len(score_elements) >= 3:
                            fixture_data["home_score"] = score_elements[0].text.strip()
                            fixture_data["away_score"] = score_elements[2].text.strip()

                        time_elem = score_container.find_element(
                            By.CSS_SELECTOR, ".text-xs"
                        )
                        fixture_data["time"] = time_elem.text.strip()

                        if fixture_data["time"] in ["FT", "AET", "PEN"]:
                            fixture_data["is_playing"] = False
                        elif (
                            fixture_data["time"] in ["HT"]
                            or fixture_data["time"].isdigit()
                        ):
                            fixture_data["is_playing"] = True

                    except Exception as e:
                        logger.debug(
                            f"No score container found (match not started?): {e}"
                        )
                        try:
                            time_div = middle_col.find_element(By.TAG_NAME, "div")
                            fixture_data["time"] = time_div.text.strip()
                            fixture_data["is_playing"] = False
                            logger.info(f"Upcoming match time: {fixture_data['time']}")
                        except Exception as e2:
                            logger.warning(
                                f"Could not extract time for upcoming match: {e2}"
                            )
                            pass

                    all_matches_data.append(fixture_data)

            except Exception as e:
                logger.error(f"Error parsing league container: {e}", exc_info=True)
                continue

        logger.info(
            f"Collected {len(all_matches_data)} fixtures, now extracting links..."
        )

        match_cards = selenium_manager.driver.find_elements(
            By.CSS_SELECTOR,
            ".m-1.border-b.border-gray-300.rounded-md.py-3.hover\\:bg-gray-300.cursor-pointer.text-primary",
        )

        logger.info(f"Found {len(match_cards)} clickable match cards")

        for i in range(min(len(all_matches_data), len(match_cards))):
            try:
                if i > 0:
                    logger.info(f"Navigating back from previous fixture...")
                    selenium_manager.driver.execute_script("window.history.go(-1)")

                    WebDriverWait(selenium_manager.driver, 15).until(
                        lambda d: "/scores" in d.current_url
                        and "/scores/football/" not in d.current_url
                    )

                    # Wait for page to be fully loaded
                    WebDriverWait(selenium_manager.driver, 15).until(
                        lambda d: d.execute_script("return document.readyState")
                        == "complete"
                    )

                    logger.info(f"Waiting for page to re-render...")
                    time.sleep(5)

                    # Wait for match cards to be present again
                    WebDriverWait(selenium_manager.driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (
                                By.CSS_SELECTOR,
                                ".m-1.border-b.border-gray-300.rounded-md.py-3.hover\\:bg-gray-300.cursor-pointer.text-primary",
                            )
                        )
                    )

                    match_cards = selenium_manager.driver.find_elements(
                        By.CSS_SELECTOR,
                        ".m-1.border-b.border-gray-300.rounded-md.py-3.hover\\:bg-gray-300.cursor-pointer.text-primary",
                    )

                if i >= len(match_cards):
                    logger.warning(
                        f"No clickable element found for fixture index {i} (found {len(match_cards)} cards)"
                    )
                    continue

                card = match_cards[i]

                selenium_manager.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", card
                )
                time.sleep(1)

                logger.info(
                    f"Clicking fixture card {i+1}/{len(all_matches_data)}: {all_matches_data[i]['home']} vs {all_matches_data[i]['away']}"
                )
                selenium_manager.driver.execute_script("arguments[0].click();", card)

                # Wait for detail page to load
                try:
                    WebDriverWait(selenium_manager.driver, 10).until(
                        lambda d: "/scores/football/" in d.current_url
                    )

                    # Wait for page to fully render
                    time.sleep(3)

                    current_url = selenium_manager.driver.current_url
                    all_matches_data[i]["link"] = current_url

                    logger.info(
                        f"✅ [{i+1}/{len(all_matches_data)}] Captured link: {current_url}"
                    )

                except TimeoutException:
                    logger.warning(f"Timeout waiting for detail page for fixture {i}")
                    all_matches_data[i]["link"] = selenium_manager.driver.current_url

            except Exception as e:
                logger.error(f"Error navigating to fixture {i}: {e}", exc_info=True)
                continue

        logger.info(f"Extracted {len(all_matches_data)} fixtures with links")

        for data in all_matches_data:
            logger.info(
                f"Fixture: {data['home']} vs {data['away']} | "
                f"Score: {data['home_score']}-{data['away_score']} | "
                f"Time: {data['time']} | "
                f"Link: {data['link'][:50] if data['link'] else 'NO LINK'}"
            )

        return all_matches_data

    except Exception as e:
        logger.error(f"Could not extract fixture data: {e}", exc_info=True)
        return []


def extract_match_events_from_detail_page(selenium_manager, fixture, match_link):
    try:
        logger.info(f"Navigating to match detail page: {match_link}")

        if not selenium_manager.safe_get(match_link):
            logger.error("Failed to load match detail page")
            return None

        WebDriverWait(selenium_manager.driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(5)

        try:
            tab_buttons = selenium_manager.driver.find_elements(
                By.CSS_SELECTOR, "button.p-2"
            )
            for tab in tab_buttons:
                if "Details" in tab.text and "bg-indigo-200" not in tab.get_attribute(
                    "class"
                ):
                    selenium_manager.driver.execute_script("arguments[0].click();", tab)
                    time.sleep(2)
                    logger.info("Switched to Details tab")
                    break
        except Exception as e:
            logger.warning(f"Could not switch to Details tab: {e}")

        match_events = {
            "home_team": {
                "team_id": str(fixture.home_team.id),
                "goals": [],
                "yellow_cards": [],
                "red_cards": [],
                "substitutions": [],
            },
            "away_team": {
                "team_id": str(fixture.away_team.id),
                "goals": [],
                "yellow_cards": [],
                "red_cards": [],
                "substitutions": [],
            },
        }

        try:
            events_container = selenium_manager.driver.find_element(
                By.CSS_SELECTOR, ".mt-2.text-gray-700.bg-white.rounded-md"
            )
        except:
            logger.warning("Could not find events container")
            return match_events

        all_event_divs = events_container.find_elements(
            By.CSS_SELECTOR, "div.space-y-2 > div"
        )

        logger.info(f"Found {len(all_event_divs)} potential event elements")

        for event_div in all_event_divs:
            if "bg-gray-300" in event_div.get_attribute("class"):
                continue

            try:
                event_content = event_div.find_element(
                    By.CSS_SELECTOR, "div.p-2.font-semibold"
                )
                event_text = event_content.text.strip()

                if not event_text:
                    continue

                event = parse_event_with_team(event_content, event_text)

                if event and "team" in event and "type" in event:
                    team = event["team"]  # 'home' or 'away'
                    event_type = event["type"]

                    if event_type == "goal":
                        event_data = {
                            "player_name": event.get("player", "Unknown"),
                            "team_id": match_events[f"{team}_team"]["team_id"],
                            "count": 1,
                        }
                        match_events[f"{team}_team"]["goals"].append(event_data)

                    elif event_type == "yellow_card":
                        event_data = {
                            "player_name": event.get("player", "Unknown"),
                            "team_id": match_events[f"{team}_team"]["team_id"],
                            "count": 1,
                        }
                        match_events[f"{team}_team"]["yellow_cards"].append(event_data)

                    elif event_type == "red_card":
                        event_data = {
                            "player_name": event.get("player", "Unknown"),
                            "team_id": match_events[f"{team}_team"]["team_id"],
                            "count": 1,
                        }
                        match_events[f"{team}_team"]["red_cards"].append(event_data)

                    elif event_type == "substitution":
                        event_data = {
                            "player_out": event.get("player_out", "Unknown"),
                            "player_in": event.get("player_in", "Unknown"),
                            "team_id": match_events[f"{team}_team"]["team_id"],
                            "minute": event.get("minute", 0),
                        }
                        match_events[f"{team}_team"]["substitutions"].append(event_data)

            except Exception as e:
                logger.warning(f"Error parsing event div: {e}")
                continue

        logger.info(
            f"Extracted events - Home: {len(match_events['home_team']['goals'])}⚽ "
            f"{len(match_events['home_team']['yellow_cards'])}🟨 "
            f"{len(match_events['home_team']['red_cards'])}🟥 "
            f"{len(match_events['home_team']['substitutions'])}🔄 | "
            f"Away: {len(match_events['away_team']['goals'])}⚽ "
            f"{len(match_events['away_team']['yellow_cards'])}🟨 "
            f"{len(match_events['away_team']['red_cards'])}🟥 "
            f"{len(match_events['away_team']['substitutions'])}🔄"
        )

        return match_events

    except Exception as e:
        logger.error(f"Error extracting match events: {e}", exc_info=True)
        return None


def parse_event_with_team(event_element, event_text):
    event = {}

    try:
        minute_match = re.search(r"(\d+)'", event_text)
        if minute_match:
            event["minute"] = int(minute_match.group(1))

        parent_html = event_element.get_attribute("outerHTML")

        if "justify-end" in parent_html or "text-end" in parent_html:
            event["team"] = "away"
        else:
            event["team"] = "home"

        # Goal detection
        if "⚽" in event_text:
            event["type"] = "goal"
            player_text = re.sub(r"^\d+'?\s*", "", event_text)
            player_text = player_text.replace("⚽", "").strip()
            event["player"] = player_text

        # Yellow card detection
        elif "🟨" in event_text:
            event["type"] = "yellow_card"
            player_text = re.sub(r"^\d+'?\s*", "", event_text)
            player_text = player_text.replace("🟨", "").strip()
            event["player"] = player_text

        # Red card detection
        elif "🟥" in event_text:
            event["type"] = "red_card"
            player_text = re.sub(r"^\d+'?\s*", "", event_text)
            player_text = player_text.replace("🟥", "").strip()
            event["player"] = player_text

        # Substitution detection
        elif "⬇️" in event_text and "⬆️" in event_text:
            event["type"] = "substitution"
            sub_text = re.sub(r"^\d+'?\s*", "", event_text)

            if "⬇️" in sub_text:
                parts = sub_text.split("⬇️")
                if len(parts) > 1:
                    out_and_in = parts[1]
                    if "⬆️" in out_and_in:
                        player_out, player_in = out_and_in.split("⬆️")
                        event["player_out"] = player_out.strip()
                        event["player_in"] = player_in.strip()
        else:
            return None

    except Exception as e:
        logger.warning(f"Error parsing event '{event_text}': {e}")
        return None

    return event


def update_match_events_in_db(fixture, match_events):
    if not match_events:
        logger.warning(f"No match events to update for fixture {fixture.id}")
        return

    try:
        all_goals = (
            match_events["home_team"]["goals"] + match_events["away_team"]["goals"]
        )
        if all_goals:
            logger.info(f"Updating {len(all_goals)} goals for fixture {fixture.id}")
            result = MatchEventService.update_goals(fixture, all_goals)
            logger.info(
                f"Goals update result: {result['updated_count']} updated, "
                f"{len(result['errors'])} errors"
            )

        # Update yellow cards
        all_yellow_cards = (
            match_events["home_team"]["yellow_cards"]
            + match_events["away_team"]["yellow_cards"]
        )

        # Update red cards
        all_red_cards = (
            match_events["home_team"]["red_cards"]
            + match_events["away_team"]["red_cards"]
        )

        if all_yellow_cards or all_red_cards:
            logger.info(
                f"Updating {len(all_yellow_cards)} yellow cards and "
                f"{len(all_red_cards)} red cards for fixture {fixture.id}"
            )
            result = MatchEventService.update_cards(
                fixture, all_yellow_cards, all_red_cards
            )
            logger.info(
                f"Cards update result: {result['updated_count']} updated, "
                f"{len(result['errors'])} errors"
            )

        # Update substitutions
        all_substitutions = (
            match_events["home_team"]["substitutions"]
            + match_events["away_team"]["substitutions"]
        )
        if all_substitutions:
            logger.info(
                f"Updating {len(all_substitutions)} substitutions for fixture {fixture.id}"
            )
            result = MatchEventService.update_substitutions(fixture, all_substitutions)
            logger.info(
                f"Substitutions update result: {result['updated_count']} updated, "
                f"{len(result['errors'])} errors"
            )

        logger.info(f"Successfully updated all match events for fixture {fixture.id}")

    except Exception as e:
        logger.error(f"Error updating match events in database: {e}", exc_info=True)


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

            # Handle postponed fixtures
            if fixture.status == "postponed":
                logger.info(
                    f"Fixture {fixture.id} was postponed, updating from live data"
                )
                fixture.match_date = timezone.now()
                fixture.status = "upcoming"
                fixture.save(update_fields=["match_date", "status"])

                if pt:
                    pt.enabled = False
                    pt.save(update_fields=["enabled"])
                    logger.info(f"Kept PeriodicTask disabled for fixture {fixture.id}")

            # Handle live matches
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

            # Handle completed matches
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

                # Update scores
                if int(data["home_score"]) > 0 or int(data["away_score"]) > 0:
                    if fixture.home_team_score != int(
                        data["home_score"]
                    ) or fixture.away_team_score != int(data["away_score"]):
                        fixture.home_team_score = int(data["home_score"])
                        fixture.away_team_score = int(data["away_score"])
                        fixture.save()
                        logger.info(
                            f"Updated scores: {fixture.home_team.name} {fixture.home_team_score} - "
                            f"{fixture.away_team_score} {fixture.away_team.name}"
                        )

                    # Extract and update match events
                    try:
                        match_events = extract_match_events_from_detail_page(
                            selenium_manager, fixture, data["link"]
                        )
                        if match_events:
                            update_match_events_in_db(fixture, match_events)
                        else:
                            logger.warning(
                                f"No match events extracted for fixture {fixture.id}"
                            )
                    except Exception as e:
                        logger.error(
                            f"Failed to extract/update match events for fixture {fixture.id}: {e}",
                            exc_info=True,
                        )

            # Handle postponed status
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
        task_name = (
            f"monitor_fixture_{fixture.id}_"
            f"{fixture.gameweek.number if fixture.gameweek else 'N/A'}"
        )
        pt = PeriodicTask.objects.filter(name=task_name, enabled=True).first()
        if pt:
            pt.enabled = False
            pt.expires = timezone.now()
            pt.save(update_fields=["enabled", "expires"])
            logger.info(f"Disabled PeriodicTask for stale fixture {fixture.id}")


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

            live_data = extract_fixture_data(selenium_manager, match_url)

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
        events_updated = 0

        # Process fixtures
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

                    # Update scores
                    if fixture.home_team_score != int(
                        data["home_score"]
                    ) or fixture.away_team_score != int(data["away_score"]):

                        fixture.home_team_score = int(data["home_score"])
                        fixture.away_team_score = int(data["away_score"])
                        updates += 1
                        fixture_updated = True

                        logger.info(
                            f"Score update: {fixture.home_team.name} "
                            f"{old_home_score}->{fixture.home_team_score}, "
                            f"{fixture.away_team.name} "
                            f"{old_away_score}->{fixture.away_team_score}"
                        )

                    # Update match events for live or completed matches
                    if data["is_playing"] or data["time"] == "FT":
                        if fixture.status != "live" and data["is_playing"]:
                            fixture.status = "live"
                            fixture_updated = True

                        try:
                            time.sleep(2)  # Brief delay

                            match_events = extract_match_events_from_detail_page(
                                selenium_manager, fixture, data["link"]
                            )

                            if match_events:
                                update_match_events_in_db(fixture, match_events)
                                events_updated += 1
                                successful_updates += 1
                                logger.info(
                                    f"Updated match events for fixture {fixture.id} "
                                    f"(status: {fixture.status})"
                                )
                            else:
                                logger.warning(
                                    f"No events found for fixture {fixture.id}"
                                )
                        except Exception as e:
                            failed_updates += 1
                            logger.error(
                                f"Failed to update match events for fixture {fixture.id}: {e}",
                                exc_info=True,
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
            f"{events_updated} event updates, "
            f"{successful_updates} successful, {failed_updates} failed"
        )

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

        finalization_result = setup_team_finalization_task(active_gameweek)

        logger.info(
            f"Created {tasks_created} new fixture tasks, "
            f"updated {tasks_updated} fixture tasks for gameweek {active_gameweek.number}. "
            f"Finalization task: {finalization_result}"
        )

        return {
            "fixture_tasks_created": tasks_created,
            "fixture_tasks_updated": tasks_updated,
            "finalization_task": finalization_result,
            "gameweek": active_gameweek.number,
        }

    except Exception as e:
        logger.error(f"Error setting up gameweek monitoring: {e}", exc_info=True)
        return f"Error setting up gameweek monitoring: {e}"


def disable_fixture(fixture):
    if fixture.status == "completed":
        task_name = f"monitor_fixture_{fixture.id}_{fixture.gameweek.number}"
        try:
            periodic_task = PeriodicTask.objects.get(name=task_name)
            if periodic_task.enabled:
                periodic_task.enabled = False
                periodic_task.expires = timezone.now()
                periodic_task.save(update_fields=["enabled", "expires"])
                logger.info(
                    f"Disabled monitoring task for completed fixture {fixture.id}"
                )
        except PeriodicTask.DoesNotExist:
            logger.debug(
                f"Periodic task {task_name} not found "
                "(already deleted or never created)"
            )
        except Exception as e:
            logger.error(f"Error disabling task {task_name}: {e}", exc_info=True)
