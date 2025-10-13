import json
import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from apps.fantasy.models import FantasyTeam, TeamSelection
from apps.kpl.models import Fixture, Gameweek
from config.settings import base

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


def setup_team_finalization_task(gameweek):
    """
    Create or update a one-time task to finalize team selections at deadline
    """
    try:
        if not gameweek.transfer_deadline:
            logger.warning(
                f"Gameweek {gameweek.number} has no transfer deadline set. "
                "Cannot schedule finalization."
            )
            return "No transfer deadline"

        current_time = timezone.now()

        if current_time >= gameweek.transfer_deadline:
            logger.info(
                f"Deadline for Gameweek {gameweek.number} has already passed. "
                "Finalizing teams immediately."
            )
            finalize_gameweek_teams.delay(str(gameweek.id))
            return "Finalized immediately (deadline passed)"

        task_name = f"finalize_teams_gw_{gameweek.number}"

        existing_task = PeriodicTask.objects.filter(name=task_name).first()

        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        if existing_task:
            existing_task.enabled = True
            existing_task.start_time = gameweek.transfer_deadline
            existing_task.expires = gameweek.transfer_deadline + timedelta(minutes=1)
            existing_task.one_off = True
            existing_task.kwargs = json.dumps({"gameweek_id": str(gameweek.id)})
            existing_task.save(
                update_fields=["enabled", "start_time", "expires", "one_off", "kwargs"]
            )
            logger.info(
                f"Updated team finalization task for Gameweek {gameweek.number} "
                f"at {gameweek.transfer_deadline}"
            )
            return "Updated"
        else:
            PeriodicTask.objects.create(
                interval=schedule,
                name=task_name,
                task="apps.kpl.tasks.gameweeks.finalize_gameweek_teams",
                args=json.dumps([]),
                kwargs=json.dumps({"gameweek_id": str(gameweek.id)}),
                start_time=gameweek.transfer_deadline,
                expires=gameweek.transfer_deadline + timedelta(minutes=1),
                one_off=True,
                enabled=True,
            )
            logger.info(
                f"Created team finalization task for Gameweek {gameweek.number} "
                f"at {gameweek.transfer_deadline}"
            )
            return "Created"

    except Exception as e:
        logger.error(f"Error setting up team finalization task: {e}", exc_info=True)
        return f"Error: {e}"


@shared_task
def finalize_gameweek_teams(gameweek_id):
    try:
        gameweek = Gameweek.objects.get(id=gameweek_id)
        logger.info(f"Starting team finalization for Gameweek {gameweek.number}")

        fantasy_teams = FantasyTeam.objects.all()

        finalized_count = 0
        created_from_previous_count = 0
        skipped_count = 0

        for team in fantasy_teams:
            try:
                result = finalize_team_for_gameweek(team, gameweek)

                if result == "finalized":
                    finalized_count += 1
                elif result == "created_from_previous":
                    created_from_previous_count += 1
                elif result == "skipped":
                    skipped_count += 1

            except Exception as e:
                logger.error(f"Error finalizing team {team.name} (ID: {team.id}): {e}")
                continue
        

        FantasyTeam.objects.update(
            transfers_available=F("free_transfers") + 1
        )
        
        logger.info(
            f"Gameweek {gameweek.number} finalization complete. "
            f"Finalized: {finalized_count}, "
            f"Created from previous: {created_from_previous_count}, "
            f"Skipped: {skipped_count}"
        )

        return {
            "gameweek": gameweek.number,
            "finalized": finalized_count,
            "created_from_previous": created_from_previous_count,
            "skipped": skipped_count,
        }

    except Gameweek.DoesNotExist:
        logger.error(f"Gameweek with ID {gameweek_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error in finalize_gameweek_teams: {e}")
        return False


@transaction.atomic
def finalize_team_for_gameweek(fantasy_team, gameweek):
    existing_selection = TeamSelection.objects.filter(
        fantasy_team=fantasy_team, gameweek=gameweek
    ).first()

    if existing_selection:
        if not existing_selection.is_finalized:
            existing_selection.is_finalized = True
            existing_selection.save(update_fields=["is_finalized"])
            logger.info(
                f"Finalized existing selection for {fantasy_team.name} "
                f"in Gameweek {gameweek.number}"
            )
            return "finalized"
        else:
            logger.debug(
                f"Selection already finalized for {fantasy_team.name} "
                f"in Gameweek {gameweek.number}"
            )
            return "skipped"

    previous_selection = get_previous_gameweek_selection(fantasy_team, gameweek)

    if not previous_selection:
        logger.warning(
            f"No previous selection found for {fantasy_team.name}. "
            f"Cannot create selection for Gameweek {gameweek.number}"
        )
        return "skipped"

    try:
        new_selection = create_selection_from_previous(
            fantasy_team, gameweek, previous_selection
        )
        logger.info(
            f"Created and finalized selection for {fantasy_team.name} "
            f"in Gameweek {gameweek.number} from Gameweek {previous_selection.gameweek.number}"
        )
        return "created_from_previous"

    except Exception as e:
        logger.error(
            f"Failed to create selection from previous for {fantasy_team.name}: {e}"
        )
        return "skipped"


def get_previous_gameweek_selection(fantasy_team, current_gameweek):
    """Get the most recent team selection before the current gameweek"""
    return (
        TeamSelection.objects.filter(
            fantasy_team=fantasy_team,
            gameweek__number__lt=current_gameweek.number,
            is_finalized=True,
        )
        .order_by("-gameweek__number")
        .first()
    )


def create_selection_from_previous(fantasy_team, gameweek, previous_selection):
    captain = previous_selection.captain
    vice_captain = previous_selection.vice_captain

    current_fantasy_players = fantasy_team.players.all()
    current_player_ids = set(fp.player.id for fp in current_fantasy_players)

    if captain.player.id not in current_player_ids:
        captain = current_fantasy_players.filter(is_starter=True).first()
        if not captain:
            captain = current_fantasy_players.first()

    if vice_captain.player.id not in current_player_ids:
        vice_captain = (
            current_fantasy_players.filter(is_starter=True)
            .exclude(id=captain.id)
            .first()
        )
        if not vice_captain:
            vice_captain = current_fantasy_players.exclude(id=captain.id).first()

    starters = current_fantasy_players.filter(is_starter=True)
    bench = current_fantasy_players.filter(is_starter=False)

    new_selection = TeamSelection.objects.create(
        fantasy_team=fantasy_team,
        gameweek=gameweek,
        formation=previous_selection.formation,
        captain=captain,
        vice_captain=vice_captain,
        is_finalized=True,
    )

    new_selection.starters.set(starters)
    new_selection.bench.set(bench)

    return new_selection


def check_current_active_gameweek(current_datetime):
    current_active_gameweek = Gameweek.objects.filter(is_active=True).first()

    if not current_active_gameweek or not current_active_gameweek.end_date:
        return False

    end_datetime = datetime.combine(
        current_active_gameweek.end_date,
        datetime.min.time(),
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

        if days_gap > 2 or teams_in_fixture & current_week_teams:
            current_week_start = current_fixture.match_date.date()
            fixtures_by_week[current_week_start] = [current_fixture]
            current_week_teams = teams_in_fixture.copy()
        else:
            fixtures_by_week[current_week_start].append(current_fixture)
            current_week_teams.update(teams_in_fixture)

    return fixtures_by_week

def calculate_transfer_deadline(fixtures, current_datetime):
    if not fixtures:
        return None

    first_match = min(fixtures, key=lambda x: x.match_date)
    transfer_deadline = first_match.match_date - timedelta(hours=2)

    if current_datetime >= transfer_deadline:
        logger.warning(
            f"Transfer deadline ({transfer_deadline}) has already passed. "
            f"Looking for next available fixtures."
        )
        return None

    return transfer_deadline

def find_or_create_gameweek_for_week(week_start, fixtures, transfer_deadline):
    existing_gameweek = None
    for fixture in fixtures:
        if fixture.gameweek:
            existing_gameweek = fixture.gameweek
            break

    first_match = min(fixtures, key=lambda x: x.match_date)
    transfer_deadline = first_match.match_date - timedelta(hours=2)

    if existing_gameweek:
        existing_gameweek.transfer_deadline = transfer_deadline
        existing_gameweek.save(update_fields=["transfer_deadline"])
        return existing_gameweek

    week_end = max(f.match_date.date() for f in fixtures)

    matching_gameweek = Gameweek.objects.filter(
        start_date__lte=week_start, end_date__gte=week_end
    ).first()

    if matching_gameweek:
        if not matching_gameweek.transfer_deadline:
            first_match = min(fixtures, key=lambda x: x.match_date)
            matching_gameweek.transfer_deadline = first_match.match_date - timedelta(hours=2)
            matching_gameweek.save(update_fields=["transfer_deadline"])
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
    try:
        gameweek.is_active = True
        gameweek.transfer_deadline = transfer_deadline
        gameweek.save()

        for fixture in fixtures:
            if not fixture.gameweek:
                fixture.gameweek = gameweek
                fixture.save()

        logger.info(
            f"Set Gameweek {gameweek.number} as active. "
            f"Transfer deadline: {transfer_deadline}"
        )
        return True
    except Exception as e:
        logger.error(f"Error activating gameweek {gameweek.number}: {e}")
        return False


def set_active_gameweek_from_date_ranges(current_datetime, current_date):
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
    try:
        gameweek_fixtures = Fixture.objects.filter(gameweek=gameweek).order_by(
            "match_date"
        )

        if gameweek_fixtures.exists():
            first_match = min(gameweek_fixtures, key=lambda x: x.match_date)
            gameweek.transfer_deadline = first_match.match_date - timedelta(hours=2)

        gameweek.is_active = True
        gameweek.save()

        logger.info(
            f"Set Gameweek {gameweek.number} as active. "
        )
        return True
    except Exception as e:
        logger.error(f"Error activating gameweek {gameweek.number}: {e}")
        return False