from celery import shared_task
import requests
import os
import logging
from bs4 import BeautifulSoup
from util.views import headers
from apps.kpl.models import Team, Fixture
from datetime import datetime

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
def get_kpl_fixtures():
    response = extract_fixtures_data(headers)
    return response
