import logging
import logging.config
import os
from datetime import datetime
from django.core.cache import cache

import requests
from bs4 import BeautifulSoup
from celery import shared_task

from apps.kpl.models import Standing, Team
from config.settings import base
from util.views import headers
from .fixtures import find_team

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


def extract_table_standings_data(headers) -> str:
    # url = os.getenv("TABLE_STANDINGS_URL")
    # if not url:
    #     logger.error("TABLE_STANDINGS_URL environment variable not set")
    #     return "Configuration error: TABLE_STANDINGS_URL not found"
    
    # Using the new URL directly as requested
    url = "https://kenyafootballdata.com/tournament_stats.php?t=uftn0043"

    current_year = datetime.now().year
    previous_year = current_year - 1
    period = f"{previous_year}-{current_year}"

    try:
        import time
        import random
        
        session = requests.Session()
        session.headers.update(headers)
        
        # Add a small random delay to mimic human behavior
        time.sleep(random.uniform(1, 3))
        
        web_content = session.get(url, timeout=30)
        logger.info(f"Request to {url} returned status code: {web_content.status_code}")
    except requests.RequestException as e:
        logger.error(f"Network error when fetching standings: {str(e)}")
        return f"Network error: {str(e)}"

    if web_content.status_code == 200:
        all_teams = Team.objects.all()
        existing_team_count = all_teams.count()
        logger.info(f"Found {existing_team_count} existing teams in database")

        Standing.objects.all().delete()

        soup = BeautifulSoup(web_content.text, "lxml")
        # The new site seems to have a single table with all data
        table_body = soup.find("tbody")
        
        if not table_body:
             # Fallback if tbody is not found, try finding the table directly
            table = soup.find("table")
            if table:
                table_body = table.find("tbody") or table

        if table_body:
            rows = table_body.find_all("tr")
            logger.info(f"Found {len(rows)} rows in the standings table")

            teams_found_in_extraction = []
            created_standings = 0

            for idx, row in enumerate(rows):
                try:
                    cols = row.find_all("td")
                    if not cols or len(cols) < 12:
                        logger.warning(f"Row {idx+1} has insufficient columns: {len(cols)}")
                        continue

                    # Extract data based on new structure:
                    # 0: Position
                    # 1: Logo
                    # 2: Team Name
                    # 3: Empty?
                    # 4: Played
                    # 5: Won
                    # 6: Drawn
                    # 7: Lost
                    # 8: GF
                    # 9: GA
                    # 10: GD
                    # 11: Points

                    position_text = cols[0].text.strip()
                    # Handle cases where position might be non-numeric or empty
                    if not position_text.isdigit():
                         logger.warning(f"Invalid position at row {idx+1}: {position_text}")
                         continue
                    position = int(position_text)

                    # Team Name
                    team_name_elem = cols[2].find("a")
                    team_name = team_name_elem.text.strip() if team_name_elem else cols[2].text.strip()

                    # Logo
                    img_elem = cols[1].find("img")
                    logo_src = img_elem["src"] if img_elem else ""
                    # Ensure full URL for logo if it's relative
                    if logo_src and not logo_src.startswith("http"):
                        # Base URL seems to be https://kenyafootballdata.com/
                        logo = f"https://kenyafootballdata.com/{logo_src}"
                    else:
                        logo = logo_src

                    logger.debug(
                        f"Processing team {idx+1}: {team_name} (Position: {position})"
                    )

                    if not team_name:
                        logger.warning(f"Could not extract team name for row {idx+1}")
                        continue

                    team, created = Team.objects.get_or_create(
                        name=team_name,
                        defaults={"logo_url": logo, "is_relegated": False},
                    )
                    teams_found_in_extraction.append(team.name)

                    if created:
                        logger.info(f"Created new team: {team_name} (marked as active)")
                    else:
                        # Update logo if we found one and the existing one is empty or different? 
                        # For now, let's stick to the logic of just reactivating if relegated.
                        # But we might want to update the logo if it's better.
                        if logo and (not team.logo_url or "kenyafootballdata" in logo):
                             team.logo_url = logo
                        
                        if team.is_relegated:
                            team.is_relegated = False
                            logger.info(f"Reactivated team: {team_name}")
                        
                        team.save()

                    try:
                        standing = Standing.objects.create(
                            position=position,
                            team=team,
                            played=int(cols[4].text.strip()),
                            wins=int(cols[5].text.strip()),
                            draws=int(cols[6].text.strip()),
                            losses=int(cols[7].text.strip()),
                            goals_for=int(cols[8].text.strip()),
                            goals_against=int(cols[9].text.strip()),
                            goal_differential=int(cols[10].text.strip()),
                            points=int(cols[11].text.strip()),
                            period=period,
                        )
                        created_standings += 1
                    except (ValueError, IndexError) as e:
                        logger.error(
                            f"Error creating standing for {team_name}: {str(e)}"
                        )

                except Exception as e:
                    logger.error(f"Error processing team row {idx+1}: {str(e)}")
                    continue

            all_teams = Team.objects.all()
            for team in all_teams:
                if team.name not in teams_found_in_extraction:
                    if not team.is_relegated:
                        team.is_relegated = True
                        team.save()
                        logger.info(f"Marked team as relegated: {team.name}")

            active_teams = Team.objects.filter(is_relegated=False)
            relegated_teams = Team.objects.filter(is_relegated=True)

            logger.info(f"Relegation status update complete:")
            logger.info(
                f"  - Active teams: {active_teams.count()} ({', '.join(active_teams.values_list('name', flat=True))})"
            )
            logger.info(f"  - Relegated teams: {relegated_teams.count()}")

            return f"Successfully updated the table standings. Processed {created_standings} rows."

        else:
            return "Table not found"

    else:
        return (
            f"Failed to retrieve the web page. Status code: {web_content.status_code}"
        )


def edit_team_logo(headers) -> str:
    url = os.getenv("TEAM_LOGOS_URL")
    if not url:
        logger.error("TEAM_LOGOS_URL environment variable not set")
        return "Configuration error: TEAM_LOGOS_URL not found"

    try:
        web_content = requests.get(url, headers=headers, verify=False, timeout=30)
    except requests.RequestException as e:
        return f"Network error: {str(e)}"

    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, "lxml")
        table = soup.find("tbody")

        if not table:
            return "Table not found on the page."

        teams = table.find_all("tr")

        updated_count = 0
        for i, team in enumerate(teams):
            try:
                name_elem = team.find("td", class_="data-name")
                full_name = name_elem.text.strip() if name_elem else ""

                img_elem = team.find("img")
                logo = img_elem["src"] if img_elem else ""

                if not full_name:
                    logger.warning(f"No team name found for row {i+1}")
                    continue

                team_obj = find_team(full_name)
                if team_obj:
                    if logo:
                        old_logo = team_obj.logo_url
                        team_obj.logo_url = logo
                        team_obj.save()
                        updated_count += 1
                    else:
                        logger.warning(f"No logo URL found for team: {full_name}")
                else:
                    logger.warning(f"No team found in database for: {full_name}")

            except Exception as e:
                logger.error(f"Error processing logo for row {i+1}: {str(e)}")
                continue

        return f"Successfully updated {updated_count} team logos."

    else:
        return (
            f"Failed to retrieve the web page. Status code: {web_content.status_code}"
        )


@shared_task
def get_kpl_table():
    try:
        first_response = extract_table_standings_data(headers)
        logger.info(f"Standings extraction result: {first_response}")
    except Exception as e:
        first_response = f"Error in extracting standings: {str(e)}"
        logger.error(f"Standings extraction failed: {str(e)}", exc_info=True)

    try:
        second_response = edit_team_logo(headers)
    except Exception as e:
        second_response = f"Error in updating team logos: {str(e)}"
        logger.error(f"Logo update failed: {str(e)}", exc_info=True)

    final_result = f"{first_response} - {second_response}"


    return final_result
