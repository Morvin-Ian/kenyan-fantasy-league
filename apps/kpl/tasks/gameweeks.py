import logging
from datetime import datetime, timedelta

from apps.kpl.models import Fixture, Gameweek
from config.settings import base

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


def check_current_active_gameweek(current_datetime):
    current_active_gameweek = Gameweek.objects.filter(is_active=True).first()

    if not current_active_gameweek or not current_active_gameweek.end_date:
        return False

    end_datetime = datetime.combine(
        current_active_gameweek.end_date,
        datetime.min.time(),  # Set to 00:00:00
        tzinfo=current_datetime.tzinfo,
    )

    if current_datetime < end_datetime:
        logger.info(
            f"Gameweek {current_active_gameweek.number} remains active. "
            f"Gameweek deadline ({end_datetime}) not yet reached."
        )
        return True

    return False


def set_active_gameweek_from_fixtures(current_datetime, current_date):
    """Set active gameweek based on upcoming fixtures"""
    upcoming_fixtures = Fixture.objects.filter(
        match_date__gte=current_datetime
    ).order_by("match_date")

    if not upcoming_fixtures.exists():
        return False

    fixtures_by_week = group_fixtures_by_week(upcoming_fixtures)
    if not fixtures_by_week:
        return False

    earliest_week = min(fixtures_by_week.keys())
    earliest_week_fixtures = fixtures_by_week[earliest_week]

    transfer_deadline = calculate_transfer_deadline(
        earliest_week_fixtures, current_datetime
    )
    if not transfer_deadline:
        return False

    gameweek = find_or_create_gameweek_for_week(
        earliest_week, earliest_week_fixtures, transfer_deadline
    )
    if not gameweek:
        return False

    return activate_gameweek_with_fixtures(
        gameweek, earliest_week_fixtures, transfer_deadline
    )


def group_fixtures_by_week(fixtures):
    """Group fixtures into gameweeks ensuring:
    1. Date proximity (≤2 days) is considered.
    2. No team plays more than once in the same gameweek.
    """
    if not fixtures:
        return {}

    sorted_fixtures = sorted(fixtures, key=lambda x: x.match_date)

    fixtures_by_week = {}
    current_week_start = sorted_fixtures[0].match_date.date()
    fixtures_by_week[current_week_start] = [sorted_fixtures[0]]

    current_week_teams = {
        sorted_fixtures[0].home_team_id,
        sorted_fixtures[0].away_team_id,
    }

    for i in range(1, len(sorted_fixtures)):
        current_fixture = sorted_fixtures[i]
        prev_fixture = sorted_fixtures[i - 1]

        days_gap = (
            current_fixture.match_date.date() - prev_fixture.match_date.date()
        ).days
        teams_in_fixture = {current_fixture.home_team_id, current_fixture.away_team_id}

        # Condition to start a new gameweek:
        # 1. Gap > 2 days
        # 2. OR either team already exists in the current week
        if days_gap > 2 or teams_in_fixture & current_week_teams:
            current_week_start = current_fixture.match_date.date()
            fixtures_by_week[current_week_start] = [current_fixture]
            current_week_teams = teams_in_fixture.copy()
        else:
            fixtures_by_week[current_week_start].append(current_fixture)
            current_week_teams.update(teams_in_fixture)

    return fixtures_by_week


def calculate_transfer_deadline(fixtures, current_datetime):
    """Calculate transfer deadline for given fixtures - based on LAST game"""
    if not fixtures:
        return None

    # Find the LAST match of the gameweek
    last_match = max(fixtures, key=lambda x: x.match_date)

    # Set deadline to 2 hours before the LAST match
    transfer_deadline = last_match.match_date - timedelta(hours=2)

    # Check if deadline hasn't passed
    if current_datetime >= transfer_deadline:
        logger.warning(
            f"Transfer deadline ({transfer_deadline}) has already passed. "
            f"Looking for next available fixtures."
        )
        return None

    return transfer_deadline


def find_or_create_gameweek_for_week(week_start, fixtures, transfer_deadline):
    """Find existing gameweek for week or create a new one"""
    existing_gameweek = None
    for fixture in fixtures:
        if fixture.gameweek:
            existing_gameweek = fixture.gameweek
            break

    if existing_gameweek:
        return existing_gameweek

    week_end = max(f.match_date.date() for f in fixtures)

    # Try to find a gameweek that covers this range
    matching_gameweek = Gameweek.objects.filter(
        start_date__lte=week_start, end_date__gte=week_end
    ).first()

    if matching_gameweek:
        return matching_gameweek

    last_gameweek = Gameweek.objects.order_by("-number").first()
    next_number = (last_gameweek.number + 1) if last_gameweek else 1

    try:
        new_gameweek = Gameweek.objects.create(
            number=next_number,
            start_date=week_start,
            end_date=week_end,
            is_active=False,
            transfer_deadline=transfer_deadline,
        )
        return new_gameweek
    except Exception as e:
        logger.error(f"Error creating new gameweek: {e}")
        return None


def activate_gameweek_with_fixtures(gameweek, fixtures, transfer_deadline):
    """Activate gameweek and assign fixtures to it"""
    try:
        gameweek.is_active = True
        gameweek.transfer_deadline = transfer_deadline
        gameweek.save()

        for fixture in fixtures:
            if not fixture.gameweek:
                fixture.gameweek = gameweek
                fixture.save()

        logger.info(
            f"Set Gameweek {gameweek.number} as active. Transfer deadline: {transfer_deadline}"
        )
        return True
    except Exception as e:
        logger.error(f"Error activating gameweek {gameweek.number}: {e}")
        return False


def set_active_gameweek_from_date_ranges(current_datetime, current_date):
    """Set active gameweek based on date ranges (fallback)"""
    current_gameweek = Gameweek.objects.filter(
        start_date__lte=current_date, end_date__gte=current_date
    ).first()

    if current_gameweek:
        return activate_existing_gameweek(current_gameweek, current_datetime)

    next_gameweek = (
        Gameweek.objects.filter(start_date__gt=current_date)
        .order_by("start_date")
        .first()
    )

    if next_gameweek:
        return activate_existing_gameweek(next_gameweek, current_datetime)

    return False


def activate_existing_gameweek(gameweek, current_datetime):
    """Activate an existing gameweek and set its transfer deadline based on LAST game"""
    try:
        gameweek_fixtures = Fixture.objects.filter(gameweek=gameweek).order_by(
            "match_date"
        )

        if gameweek_fixtures.exists():
            last_match = gameweek_fixtures.last()
            transfer_deadline = last_match.match_date - timedelta(hours=2)
            gameweek.transfer_deadline = transfer_deadline

        gameweek.is_active = True
        gameweek.save()

        logger.info(
            f"Set Gameweek {gameweek.number} as active based on date range. Transfer deadline: {transfer_deadline}"
        )
        return True
    except Exception as e:
        logger.error(f"Error activating gameweek {gameweek.number}: {e}")
        return False
