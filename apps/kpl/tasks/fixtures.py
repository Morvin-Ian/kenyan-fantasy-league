import logging
import os
from datetime import datetime
from django.utils import timezone
from datetime import timedelta

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
        
        upcoming_fixtures = Fixture.objects.filter(
            match_date__gte=current_datetime,
            status="upcoming"
        ).order_by("match_date")
        
        if upcoming_fixtures.exists():
            # Group upcoming fixtures by week
            fixtures_by_week = {}
            
            for fixture in upcoming_fixtures:
                # Get the week start (Monday) for this fixture
                fixture_date = fixture.match_date.date()
                
                week_start = fixture_date - timedelta(days=fixture_date.weekday())
                
                if week_start not in fixtures_by_week:
                    fixtures_by_week[week_start] = []
                fixtures_by_week[week_start].append(fixture)
            
            # Get the earliest week with fixtures
            earliest_week = min(fixtures_by_week.keys())
            earliest_week_fixtures = fixtures_by_week[earliest_week]
            
            # Find the first match of the week to set transfer deadline
            first_match = min(earliest_week_fixtures, key=lambda x: x.match_date)
            transfer_deadline = first_match.match_date - timedelta(hours=2)
            
            # Check if any fixture in this week already has a gameweek assigned
            existing_gameweek = None
            for fixture in earliest_week_fixtures:
                if fixture.gameweek:
                    existing_gameweek = fixture.gameweek            # Check if any fixture in this week already has a gameweek assigned

                    break
            
            if existing_gameweek:
                existing_gameweek.is_active = True
                existing_gameweek.transfer_deadline = transfer_deadline
                existing_gameweek.save()
                
                # Assign all fixtures in this week to the same gameweek
                for fixture in earliest_week_fixtures:
                    if not fixture.gameweek:
                        fixture.gameweek = existing_gameweek
                        fixture.save()
                
                logger.info(f"Set Gameweek {existing_gameweek.number} as active based on earliest week's fixtures. Transfer deadline: {transfer_deadline}")
                return f"Active gameweek set: Gameweek {existing_gameweek.number}"
            
            else:
                # Find or create a gameweek for this week
                week_end = earliest_week + timedelta(days=6)  # Sunday of the same week
                
                # Look for existing gameweek that covers this week
                matching_gameweek = Gameweek.objects.filter(
                    start_date__lte=earliest_week,
                    end_date__gte=week_end
                ).first()
                
                if not matching_gameweek:
                    # Look for a gameweek that overlaps with any day in this week
                    matching_gameweek = Gameweek.objects.filter(
                        start_date__lte=week_end,
                        end_date__gte=earliest_week
                    ).first()
                
                if matching_gameweek:
                    matching_gameweek.is_active = True
                    matching_gameweek.transfer_deadline = transfer_deadline
                    matching_gameweek.save()
                    
                    # Assign all fixtures in this week to this gameweek
                    for fixture in earliest_week_fixtures:
                        fixture.gameweek = matching_gameweek
                        fixture.save()
                    
                    logger.info(f"Set Gameweek {matching_gameweek.number} as active for week starting {earliest_week}. Transfer deadline: {transfer_deadline}")
                    return f"Active gameweek set: Gameweek {matching_gameweek.number}"
                
                else:
                    # Create a new gameweek for this week
                    last_gameweek = Gameweek.objects.order_by('-number').first()
                    next_number = (last_gameweek.number + 1) if last_gameweek else 1
                    
                    new_gameweek = Gameweek.objects.create(
                        number=next_number,
                        start_date=earliest_week,
                        end_date=week_end,
                        is_active=True,
                        transfer_deadline=transfer_deadline
                    )
                    
                    # Assign all fixtures in this week to the new gameweek
                    for fixture in earliest_week_fixtures:
                        fixture.gameweek = new_gameweek
                        fixture.save()
                    
                    logger.info(f"Created and set Gameweek {new_gameweek.number} as active for week starting {earliest_week}. Transfer deadline: {transfer_deadline}")
                    return f"Active gameweek set: Gameweek {new_gameweek.number}"
        
        # If no upcoming fixtures, find current gameweek based on date range
        current_gameweek = Gameweek.objects.filter(
            start_date__lte=current_date,
            end_date__gte=current_date
        ).first()
        
        if current_gameweek:
            # Update transfer deadline if there are fixtures for this gameweek
            gameweek_fixtures = Fixture.objects.filter(
                gameweek=current_gameweek,
                status="upcoming"
            ).order_by("match_date")
            
            if gameweek_fixtures.exists():
                first_match = gameweek_fixtures.first()
                transfer_deadline = first_match.match_date - timedelta(hours=2)
                current_gameweek.transfer_deadline = transfer_deadline
            
            current_gameweek.is_active = True
            current_gameweek.save()
            logger.info(f"Set Gameweek {current_gameweek.number} as active based on current date range.")
            return f"Active gameweek set: Gameweek {current_gameweek.number}"
        
        # If no current gameweek, find the next upcoming gameweek
        next_gameweek = Gameweek.objects.filter(
            start_date__gt=current_date
        ).order_by("start_date").first()
        
        if next_gameweek:
            # Update transfer deadline if there are fixtures for this gameweek
            gameweek_fixtures = Fixture.objects.filter(
                gameweek=next_gameweek,
                status="upcoming"
            ).order_by("match_date")
            
            if gameweek_fixtures.exists():
                first_match = gameweek_fixtures.first()
                transfer_deadline = first_match.match_date - timedelta(hours=2)
                next_gameweek.transfer_deadline = transfer_deadline
            
            next_gameweek.is_active = True
            next_gameweek.save()
            logger.info(f"Set Gameweek {next_gameweek.number} as active (next upcoming gameweek).")
            return f"Active gameweek set: Gameweek {next_gameweek.number}"
        
        logger.warning("No suitable gameweek found to set as active.")
        return "No suitable gameweek found to set as active."
        
    except Exception as e:
        logger.error(f"Error updating active gameweek: {e}")
        return f"Error updating active gameweek: {e}"    

@shared_task
def get_kpl_fixtures():
    response = extract_fixtures_data(headers)
    return response
