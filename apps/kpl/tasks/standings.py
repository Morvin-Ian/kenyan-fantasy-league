import logging
import logging.config
import os
from datetime import datetime

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
    url = os.getenv("TABLE_STANDINGS_URL")
    if not url:
        logger.error("TABLE_STANDINGS_URL environment variable not set")
        return "Configuration error: TABLE_STANDINGS_URL not found"

    current_year = datetime.now().year
    previous_year = current_year - 1
    period = f"{previous_year}-{current_year}"

    try:
        web_content = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        return f"Network error: {str(e)}"

    if web_content.status_code == 200:
        all_teams = Team.objects.all()
        existing_team_count = all_teams.count()
        logger.info(f"Found {existing_team_count} existing teams in database")

        # Clear existing standings
        Standing.objects.all().delete()

        soup = BeautifulSoup(web_content.text, "lxml")
        tables = soup.find_all("tbody", class_="Table__TBODY")
        logger.info(f"Found {len(tables)} table bodies on the page")

        if tables and len(tables) > 1:
            first_table = tables[0].find_all("tr")
            second_table = tables[1].find_all("tr")

            team_stats = []
            for i, row in enumerate(second_table):
                data_rows = row.find_all("td")
                if len(data_rows) >= 8:
                    stats = [
                        data_rows[0].text.strip(),  # Played
                        data_rows[1].text.strip(),  # Won
                        data_rows[2].text.strip(),  # Drawn
                        data_rows[3].text.strip(),  # Lost
                        data_rows[4].text.strip(),  # Goals For
                        data_rows[5].text.strip(),  # Goals Against
                        data_rows[6].text.strip(),  # Goal Difference
                        data_rows[7].text.strip(),  # Points
                    ]
                    team_stats.append(stats)
                else:
                    logger.warning(
                        f"Row {i+1} in statistics table has insufficient columns ({len(data_rows)})"
                    )

            teams_found_in_extraction = []
            created_standings = 0

            for idx, row in enumerate(first_table):
                try:
                    position_elem = row.find("span", class_="team-position")
                    position = position_elem.text if position_elem else "N/A"

                    abbr_elem = row.find("abbr")
                    team_name = abbr_elem["title"] if abbr_elem else "N/A"

                    img_elem = row.find("img")
                    logo = img_elem["src"] if img_elem else "N/A"

                    logger.debug(
                        f"Processing team {idx+1}: {team_name} (Position: {position})"
                    )

                    if team_name == "N/A":
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
                        # Make sure team is marked as active if found in extraction
                        if team.is_relegated:
                            team.is_relegated = False
                            team.save()
                            logger.info(f"Reactivated team: {team_name}")

                    # Add standings entry if stats available
                    if idx < len(team_stats) and position != "N/A":
                        stats = team_stats[idx]
                        try:
                            standing = Standing.objects.create(
                                position=int(position),
                                team=team,
                                played=int(stats[0]),
                                wins=int(stats[1]),
                                draws=int(stats[2]),
                                losses=int(stats[3]),
                                goals_for=int(stats[4]),
                                goals_against=int(stats[5]),
                                goal_differential=int(stats[6]),
                                points=int(stats[7]),
                                period=period,
                            )
                            created_standings += 1
                        except (ValueError, IndexError) as e:
                            logger.error(
                                f"Error creating standing for {team_name}: {str(e)}"
                            )
                    else:
                        logger.warning(
                            f"No statistics available for team {team_name} at index {idx}"
                        )

                except Exception as e:
                    logger.error(f"Error processing team row {idx+1}: {str(e)}")
                    continue

            # After processing all teams, mark those not found as relegated
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

            if relegated_teams.exists():
                relegated_names = ", ".join(
                    relegated_teams.values_list("name", flat=True)
                )
                logger.info(f"  - Teams marked as relegated: {relegated_names}")

            return "Successfully updated the table standings."

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
