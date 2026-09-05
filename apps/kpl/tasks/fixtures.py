"""Team and player name matching, and active-gameweek bookkeeping.

The fixtures scraper that used to live here has been replaced by
``apps.kpl.tasks.sync.sync_fixtures``. What remains are the fuzzy lookups the
rest of the app resolves scraped names through — ``find_team`` and
``find_player`` are used by the live-match monitor, the match-event service and
fantasy point scoring.
"""

import logging
import logging.config
import re
from difflib import get_close_matches
from typing import Optional

from celery import shared_task
from django.utils import timezone

from apps.kpl.models import Gameweek, Player, Team
from config.settings import base

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


def generate_name_variants(name: str) -> list[str]:
    variants = []
    name = name.strip()

    variants.append(name)

    no_initials = re.sub(r"\b[A-Z]\.\s*", "", name)
    if no_initials != name:
        variants.append(no_initials)

    parts = name.split()
    if len(parts) == 2:
        variants.append(f"{parts[1]} {parts[0]}")

    for prefix in ["Jr.", "Sr.", "II", "III"]:
        if name.endswith(prefix):
            variants.append(name.replace(prefix, "").strip())

    return list(set(variants))


def clean_player_name(name: str) -> Optional[str]:
    """
    Clean player name by removing minute markers and extra whitespace.

    Examples:
        "Elvis Noor  54'" -> "Elvis Noor"
        "Christofer Kaloti  84'" -> "Christofer Kaloti"
        "45'" -> None
        "  John Doe  " -> "John Doe"

    Args:
        name: Raw player name from scraper

    Returns:
        Cleaned name or None if name is invalid
    """
    if not name:
        return None

    cleaned = re.sub(r"\s*\d+'\s*$", "", name)

    cleaned = cleaned.strip()

    # If the entire string was just a minute marker (e.g., "45'"), return None
    if not cleaned or re.match(r"^\d+'$", cleaned):
        return None

    return cleaned


def create_missing_player(player_name: str, team: Team) -> Player:
    player = Player.objects.create(
        name=player_name,
        team=team,
        position="MID",
        current_value=5.5,
        jersey_number=None,
        age=None,
    )

    logger.warning(
        f"AUTO-CREATED PLAYER: '{player_name}' for team '{team.name}' "
        f"(position=MID, value=5.5). Please verify and update position if needed."
    )

    return player


def find_player(
    player_name: str,
    team_id: Optional[str] = None,
    team_name: Optional[str] = None,
    auto_create: bool = False,
) -> Player | None:
    if not player_name or not player_name.strip():
        logger.warning("Empty player name provided")
        return None

    cleaned_name = clean_player_name(player_name)
    if not cleaned_name:
        logger.warning(f"Player name '{player_name}' became empty after cleaning")
        return None

    player_name = cleaned_name

    require_team_match = bool(team_id or team_name)

    if require_team_match:
        logger.debug(
            f"STRICT MODE: Searching for '{player_name}' with team requirement"
        )

    if team_id:
        base_queryset = Player.objects.filter(team__id=team_id)
        logger.debug(f"   Filtered by team ID: {team_id}")
    elif team_name:
        base_queryset = Player.objects.filter(team__name__icontains=team_name)
        logger.debug(f"   Filtered by team name: {team_name}")
    else:
        base_queryset = Player.objects.all()
        logger.debug("   No team filter - searching all players")

    exact_match = base_queryset.filter(name__iexact=player_name).first()
    if exact_match:
        logger.debug(
            f"Found exact match for '{player_name}': {exact_match.name} (Team: {exact_match.team.name})"
        )
        return exact_match

    all_player_names = list(base_queryset.values_list("name", flat=True))
    if all_player_names:
        matches = get_close_matches(
            player_name.lower(), [p.lower() for p in all_player_names], n=1, cutoff=0.85
        )

        if matches:
            found_player = base_queryset.filter(name__iexact=matches[0]).first()
            if found_player:
                logger.debug(
                    f"Found close match for '{player_name}': {found_player.name} (Team: {found_player.team.name})"
                )
                return found_player

    name_variants = generate_name_variants(player_name)
    logger.debug(f"   Trying variants: {name_variants}")

    for variant in name_variants:
        variant_match = base_queryset.filter(name__iexact=variant).first()
        if variant_match:
            logger.debug(
                f"Found variant match for '{player_name}': {variant_match.name} (variant: {variant}, Team: {variant_match.team.name})"
            )
            return variant_match

    name_parts = [part.strip() for part in player_name.split() if len(part.strip()) > 1]

    if len(name_parts) > 1:
        logger.debug(f"   Trying partial name matching for parts: {name_parts}")

        for i, part in enumerate(name_parts):
            part_matches = base_queryset.filter(name__icontains=part)

            if part_matches.count() == 1:
                found_player = part_matches.first()
                logger.debug(
                    f"Found unique partial match for '{player_name}': {found_player.name} (using part: '{part}', Team: {found_player.team.name})"
                )
                return found_player
            elif part_matches.count() > 1:
                for other_part in name_parts:
                    if other_part != part:
                        disambiguated = part_matches.filter(name__icontains=other_part)
                        if disambiguated.count() == 1:
                            found_player = disambiguated.first()
                            logger.debug(
                                f"Found disambiguated match for '{player_name}': {found_player.name} (using parts: '{part}' + '{other_part}', Team: {found_player.team.name})"
                            )
                            return found_player

    if all_player_names and len(player_name) > 3:
        matches = get_close_matches(
            player_name.lower(), [p.lower() for p in all_player_names], n=1, cutoff=0.75
        )

        if matches:
            found_player = base_queryset.filter(name__iexact=matches[0]).first()
            if found_player:
                logger.debug(
                    f"Found fuzzy match for '{player_name}': {found_player.name} (Team: {found_player.team.name}) - Consider verifying"
                )
                return found_player

    # Player not found - auto-create
    if auto_create and team_id:
        try:
            team = Team.objects.get(id=team_id)
            new_player = create_missing_player(player_name, team)
            return new_player
        except Team.DoesNotExist:
            logger.error(
                f"Cannot auto-create player '{player_name}': Team with id {team_id} not found"
            )
            return None
        except Exception as e:
            logger.error(f"Error auto-creating player '{player_name}': {e}")
            return None

    if require_team_match:
        team_info = f"team_id={team_id}" if team_id else f"team_name={team_name}"
        logger.warning(f"Player not found: '{player_name}' in {team_info}")
    else:
        logger.warning(f"Player not found: '{player_name}'")

    similar_players = base_queryset.filter(name__icontains=player_name[:4])[:5]
    if similar_players:
        logger.debug(
            f"   Similar players in {'specified team' if require_team_match else 'database'}: {[f'{p.name} ({p.team.name})' for p in similar_players]}"
        )

    return None


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
