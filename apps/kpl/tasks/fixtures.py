import logging
import os
from datetime import datetime
from difflib import get_close_matches

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone

from apps.kpl.models import Fixture, Gameweek, Player, Team
from config.settings import base
from util.views import headers

from .gameweeks import (
    check_current_active_gameweek,
    set_active_gameweek_from_date_ranges,
    set_active_gameweek_from_fixtures,
)
from .live_games import setup_gameweek_monitoring

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


def find_team(team_name: str) -> Team | None:
    team_name = team_name.strip().lower()

    cleaned_name = clean_team_name(team_name)

    all_teams = list(Team.objects.values_list("name", flat=True))

    for db_team in all_teams:
        if cleaned_name == clean_team_name(db_team):
            return Team.objects.get(name=db_team)

    match = get_close_matches(
        cleaned_name, [clean_team_name(t) for t in all_teams], n=1, cutoff=0.4
    )

    if match:
        for db_team in all_teams:
            if clean_team_name(db_team) == match[0]:
                return Team.objects.get(name=db_team)

    return None


def clean_team_name(name: str) -> str:
    """Clean and normalize team names for better matching"""
    name = name.strip().lower()

    replacements = {
        "k-": "kariobangi ",
        "fc ": "",
        " fc": "",
        "afc ": "",
        " afc": "",
        " united": "",
        " city": "",
        " stars": "",
        " sugar": "",
        " ": "",
        "-": "",
    }

    cleaned = name
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    return cleaned


from difflib import get_close_matches
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def find_player(player_name: str, team_id: Optional[str] = None, team_name: Optional[str] = None) -> Player | None:
    if not player_name or not player_name.strip():
        logger.warning(f"Empty player name provided")
        return None
        
    player_name = player_name.strip()
    
    base_queryset = Player.objects.all()
    
    if team_id:
        base_queryset = base_queryset.filter(team__id=team_id)  
        logger.debug(f"   Filtered by team ID: {team_id}")
    elif team_name:
        base_queryset = base_queryset.filter(team__name__icontains=team_name) 
        logger.debug(f"   Filtered by team name: {team_name}")
    
 
    exact_match = base_queryset.filter(name__iexact=player_name).first()
    if exact_match:
        logger.debug(f"✅ Found exact match for '{player_name}': {exact_match.name}")
        return exact_match
    
    if team_id or team_name:
        logger.debug(f"   No match with team filter, trying without team filter...")
        fallback_match = Player.objects.filter(name__iexact=player_name).first()
        if fallback_match:
            logger.debug(f"✅ Found exact match without team filter for '{player_name}': {fallback_match.name}")
            return fallback_match
    
    # 3. Try close matches with team context
    all_player_names = list(base_queryset.values_list("name", flat=True))
    if all_player_names:
        match = get_close_matches(
            player_name.lower(), 
            [p.lower() for p in all_player_names], 
            n=1, 
            cutoff=0.8
        )
        
        if match:
            found_player = base_queryset.filter(name__iexact=match[0]).first()
            if found_player:
                logger.debug(f"✅ Found close match for '{player_name}': {found_player.name}")
                return found_player
    
    name_variants = generate_name_variants(player_name)
    
    for variant in name_variants:
        variant_match = base_queryset.filter(name__iexact=variant).first()
        if variant_match:
            logger.debug(f"✅ Found variant match for '{player_name}': {variant_match.name} (variant: {variant})")
            return variant_match
        
        if team_id or team_name:
            variant_match_fallback = Player.objects.filter(name__iexact=variant).first()
            if variant_match_fallback:
                logger.debug(f"✅ Found variant match without team filter for '{player_name}': {variant_match_fallback.name} (variant: {variant})")
                return variant_match_fallback
    
    name_parts = [part.strip() for part in player_name.split() if len(part.strip()) > 1]
    
    if len(name_parts) > 1:
        logger.debug(f"   Trying partial name matching for parts: {name_parts}")
        
        for i, part in enumerate(name_parts):
            part_matches = base_queryset.filter(name__icontains=part)
            
            if part_matches.count() == 1:
                found_player = part_matches.first()
                logger.debug(f"✅ Found unique partial match for '{player_name}': {found_player.name} (using part: '{part}')")
                return found_player
            elif part_matches.count() > 1:
                for other_part in name_parts:
                    if other_part != part:
                        disambiguated = part_matches.filter(name__icontains=other_part)
                        if disambiguated.count() == 1:
                            found_player = disambiguated.first()
                            logger.debug(f"✅ Found disambiguated match for '{player_name}': {found_player.name} (using parts: '{part}' + '{other_part}')")
                            return found_player
        
        if (team_id or team_name) and len(name_parts) > 1:
            for part in name_parts:
                part_matches = Player.objects.filter(name__icontains=part)
                if part_matches.count() == 1:
                    found_player = part_matches.first()
                    logger.debug(f"✅ Found unique partial match without team filter for '{player_name}': {found_player.name} (using part: '{part}')")
                    return found_player
    
    if team_id or team_name:
        logger.debug(f"   No match with team context, trying broad search...")
        all_players_broad = list(Player.objects.values_list("name", flat=True))
        match = get_close_matches(
            player_name.lower(), 
            [p.lower() for p in all_players_broad], 
            n=1, 
            cutoff=0.7
        )
        
        if match:
            found_player = Player.objects.filter(name__iexact=match[0]).first()
            if found_player:
                logger.debug(f"✅ Found broad match for '{player_name}': {found_player.name}")
                return found_player
    
    logger.warning(f"❌ Player not found: '{player_name}'")
    
    similar_players = Player.objects.filter(name__icontains=player_name[:4])[:5]
    if similar_players:
        logger.debug(f"   Similar players: {[p.name for p in similar_players]}")
    
    return None


def generate_name_variants(full_name: str) -> list:
    name_parts = [part.strip() for part in full_name.split() if part.strip()]
    variants = []
    
    if len(name_parts) >= 2:
        variants.extend([
            f"{name_parts[0]} {name_parts[-1]}", 
            f"{name_parts[-1]} {name_parts[0]}",  
        ])
        
        if len(name_parts) == 3:
            variants.extend([
                f"{name_parts[0]} {name_parts[1]}",  
                f"{name_parts[0]} {name_parts[2]}", 
                f"{name_parts[1]} {name_parts[2]}",
            ])
    
    clean_name = ''.join(c for c in full_name if c.isalnum() or c.isspace())
    if clean_name != full_name:
        variants.append(clean_name)
    
    variants = [v for v in set(variants) if v != full_name]
    
    logger.debug(f"   Generated name variants for '{full_name}': {variants}")
    return variants

def extract_fixtures_data(headers) -> bool:
    url = os.getenv("TEAM_FIXTURES_URL")

    try:
        web_content = requests.get(url, headers=headers, verify=False)
    except requests.RequestException as e:
        logger.error(f"Error fetching fixtures: {e}")
        return False

    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, "lxml")
        table = soup.find("table", class_="sp-event-blocks")
        if not table:
            logger.error("No fixtures table found on the page.")
            return False

        table_rows = table.find_all("tr")[1:]

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

            if timezone.is_naive(match_datetime):
                match_datetime = timezone.make_aware(match_datetime)

            try:
                existing_fixture = Fixture.objects.filter(
                    home_team=home_team, away_team=away_team, venue=venue
                ).first()

                if existing_fixture:
                    updated = False
                    if match_datetime == "Postponed":
                        existing_fixture.status = "postponed"
                        updated = True

                    if (
                        match_datetime != "Postponed"
                        and existing_fixture.match_date != match_datetime
                    ):
                        existing_fixture.match_date = match_datetime
                        updated = True

                    if updated:
                        existing_fixture.save()
                        fixtures_updated += 1
                        logger.info(
                            f"Updated fixture: {home_team_name} vs {away_team_name} on {match_datetime}"
                        )
                else:
                    status = (
                        "upcoming" if match_datetime >= timezone.now() else "completed"
                    )

                    Fixture.objects.create(
                        home_team=home_team,
                        away_team=away_team,
                        match_date=match_datetime,
                        venue=venue,
                        status=status,
                    )
                    fixtures_created += 1
                    logger.info(
                        f"Created new fixture: {home_team_name} vs {away_team_name} on {match_datetime}"
                    )

            except Exception as e:
                logger.error(f"Error creating or updating fixture: {e}")
        logger.info(
            f"Successfully processed KPL fixtures: {fixtures_created} created, {fixtures_updated} updated"
        )
        return True
    else:
        logger.error(
            f"Failed to retrieve the web page. Status code: {web_content.status_code}"
        )
        return False


@shared_task
def update_active_gameweek():
    try:
        current_datetime = timezone.now()
        current_date = current_datetime.date()

        if check_current_active_gameweek(current_datetime):
            setup_gameweek_monitoring.delay()
            return True

        Gameweek.objects.update(is_active=False)

        if set_active_gameweek_from_fixtures(current_datetime, current_date):
            setup_gameweek_monitoring.delay()
            return True

        # Fallback: try to set active gameweek based on date ranges
        if set_active_gameweek_from_date_ranges(current_datetime, current_date):
            setup_gameweek_monitoring.delay()
            return True

        logger.warning("No suitable gameweek found to set as active.")
        return False

    except Exception as e:
        logger.error(f"Error updating active gameweek: {e}")
        return False


@shared_task
def get_kpl_fixtures():
    response = extract_fixtures_data(headers)
    return response
