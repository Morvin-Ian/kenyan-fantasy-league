import logging
import os
from datetime import datetime
from django.utils import timezone

import requests
from bs4 import BeautifulSoup
from celery import shared_task

from apps.kpl.models import Fixture, Team, Gameweek
from util.views import headers

logger = logging.getLogger(__name__)


def find_team(team_name: str) -> Team | None:
    words = team_name.split()
    words_sorted_by_length = sorted(words, key=len, reverse=True)

    for word in words_sorted_by_length:
        team = Team.objects.filter(name__icontains=word).first()
        if team:
            return team
    return None


def extract_fixtures_data(headers) -> str:
    url = os.getenv("TEAM_FIXTURES_URL")

    try:
        web_content = requests.get(url, headers=headers, verify=False)
    except requests.RequestException as e:
        logger.error(f"Error fetching fixtures: {e}")
        return "Request to fetch fixtures failed"

    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, "lxml")
        table = soup.find("table", class_="sp-event-blocks")
        if not table:
            logger.error("No fixtures table found on the page.")
            return "No fixture table found"

        table_rows = table.find_all("tr")[1:]

        # Removed the line that deletes all fixtures
        # Instead, we'll track new fixtures and update existing ones
        fixtures_updated = 0
        fixtures_created = 0

        for row in table_rows:
            table_data = row.find("td")
            links = table_data.find_all("a")
            if len(links) < 3:
                logger.error("Insufficient match data in row; skipping")
                continue

            date = links[0].text
            time = links[1].text
            match_text = links[2].text

            match_datetime_str = f"{date} {time}"
            try:
                match_datetime = datetime.strptime(
                    match_datetime_str, "%B %d, %Y %H:%M"
                )
            except ValueError:
                try:
                    match_datetime = datetime.strptime(
                        match_datetime_str, "%b %d, %Y %H:%M"
                    )
                except ValueError:
                    logger.error(f"Date parsing failed for: {match_datetime_str}")
                    continue

            try:
                home_team_name, away_team_name = match_text.split("vs")
            except ValueError:
                logger.error(
                    f"Could not split team names from match text: '{match_text}'"
                )
                continue

            home_team = find_team(home_team_name.strip())
            away_team = find_team(away_team_name.strip())
            if not home_team or not away_team:
                logger.error(
                    f"Skipping fixture: No team found for home='{home_team_name}' or away='{away_team_name}'"
                )
                continue

            venue_div = table_data.find("div", class_="sp-event-venue")
            venue = venue_div.text.strip() if venue_div else "Unknown"

            try:
                existing_fixture = Fixture.objects.filter(
                    home_team=home_team, away_team=away_team, venue=venue
                ).first()

                if existing_fixture:
                    if existing_fixture.match_date != match_datetime:
                        existing_fixture.match_date = match_datetime
                        existing_fixture.save()
                        fixtures_updated += 1
                        logger.info(
                            f"Updated fixture: {home_team_name} vs {away_team_name} on {match_datetime}"
                        )
                else:
                    Fixture.objects.create(
                        home_team=home_team,
                        away_team=away_team,
                        match_date=match_datetime,
                        venue=venue,
                        status="upcoming",
                    )
                    fixtures_created += 1
                    logger.info(
                        f"Created new fixture: {home_team_name} vs {away_team_name} on {match_datetime}"
                    )
            except Exception as e:
                logger.error(f"Error creating or updating fixture: {e}")

        return f"Successfully processed KPL fixtures: {fixtures_created} created, {fixtures_updated} updated"
    else:
        logger.error(
            f"Failed to retrieve the web page. Status code: {web_content.status_code}"
        )
        return (
            f"Failed to retrieve the web page. Status code: {web_content.status_code}"
        )
        

@shared_task
def update_active_gameweek():
    try:
        current_datetime = timezone.now()
        current_date = current_datetime.date()

        Gameweek.objects.update(is_active=False)

        # First, try to find the active gameweek based on Gameweek start_date and end_date
        active_gameweek = Gameweek.objects.filter(
            start_date__lte=current_date,
            end_date__gte=current_date
        ).first()

        if active_gameweek:
            active_gameweek.is_active = True
            active_gameweek.save()
            logger.info(f"Set Gameweek {active_gameweek.number} as active based on date range.")
            return f"Active gameweek set: Gameweek {active_gameweek.number}"

        # If no gameweek is found based on date range, check fixtures
        upcoming_fixtures = Fixture.objects.filter(
            match_date__gte=current_datetime,
            status="upcoming"
        ).order_by("match_date")

        if not upcoming_fixtures:
            logger.warning("No upcoming fixtures found to determine gameweek.")
            return "No upcoming fixtures found to determine gameweek."

        # Get the earliest upcoming fixture
        earliest_fixture = upcoming_fixtures.first()

        # Try to find or assign a gameweek for this fixture
        if earliest_fixture.gameweek:
            earliest_fixture.gameweek.is_active = True
            earliest_fixture.gameweek.save()
            logger.info(f"Set Gameweek {earliest_fixture.gameweek.number} as active based on earliest fixture.")
            return f"Active gameweek set: Gameweek {earliest_fixture.gameweek.number}"

        # If the fixture doesn't have a gameweek, find the closest gameweek by date
        closest_gameweek = Gameweek.objects.filter(
            start_date__lte=earliest_fixture.match_date.date(),
            end_date__gte=earliest_fixture.match_date.date()
        ).first()

        if closest_gameweek:
            closest_gameweek.is_active = True
            closest_gameweek.save()
            # Optionally, assign the fixture to this gameweek
            earliest_fixture.gameweek = closest_gameweek
            earliest_fixture.save()
            logger.info(f"Set Gameweek {closest_gameweek.number} as active and assigned to fixture.")
            return f"Active gameweek set: Gameweek {closest_gameweek.number}"

        # If no gameweek matches, create a new one (optional, depending on your requirements)
        logger.warning("No matching gameweek found for the earliest fixture.")
        return "No matching gameweek found for the earliest fixture."

    except Exception as e:
        logger.error(f"Error updating active gameweek: {e}")
        return f"Error updating active gameweek: {e}"

@shared_task
def get_kpl_fixtures():
    response = extract_fixtures_data(headers)
    return response
