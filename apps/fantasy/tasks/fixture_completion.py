import logging
from typing import Dict

from celery import shared_task
from django.db import transaction

from apps.fantasy import scoring
from apps.fantasy.models import PlayerPerformance
from apps.fantasy.services import scoring_engine
from apps.kpl.models import Fixture, Team
from apps.kpl.services.match_events import FixtureValidator

logger = logging.getLogger(__name__)


@shared_task
def process_clean_sheets_on_completion(fixture_id):
    """
    Process clean sheets when a fixture is marked as complete.
    Awards points to GKP, DEF, and MID who played and kept a clean sheet.
    Handles captain/vice-captain doubling and updates fantasy team totals.
    """
    try:
        fixture = Fixture.objects.get(id=fixture_id)

        if fixture.status != "completed":
            logger.warning(
                f"Fixture {fixture_id} is not completed. Status: {fixture.status}"
            )
            return {"success": False, "message": "Fixture not completed"}

        logger.info(
            f"Processing clean sheets for {FixtureValidator.get_fixture_summary(fixture)}"
        )

        clean_sheet_teams = []

        if fixture.away_team_score == 0:
            clean_sheet_teams.append({"team": fixture.home_team, "side": "home"})
            logger.info(
                f"{fixture.home_team.name} kept a clean sheet (0 goals conceded)"
            )

        if fixture.home_team_score == 0:
            clean_sheet_teams.append({"team": fixture.away_team, "side": "away"})
            logger.info(
                f"{fixture.away_team.name} kept a clean sheet (0 goals conceded)"
            )

        if not clean_sheet_teams:
            logger.info("No clean sheets in this fixture")
            return {"success": True, "message": "No clean sheets", "updated_players": 0}

        # Process clean sheets for each team
        total_updated = 0
        results = []

        for cs_team_data in clean_sheet_teams:
            result = _process_team_clean_sheet(fixture, cs_team_data["team"])
            total_updated += result["updated_count"]
            results.append(result)

        logger.info(f"Clean sheet processing complete: {total_updated} players updated")

        return {
            "success": True,
            "fixture_id": str(fixture_id),
            "teams_with_clean_sheets": [cs["team"].name for cs in clean_sheet_teams],
            "total_players_updated": total_updated,
            "details": results,
        }

    except Fixture.DoesNotExist:
        logger.error(f"Fixture {fixture_id} not found")
        return {"success": False, "message": f"Fixture {fixture_id} not found"}
    except Exception as e:
        logger.error(
            f"Error processing clean sheets for fixture {fixture_id}: {e}",
            exc_info=True,
        )
        return {"success": False, "message": str(e)}


def _process_team_clean_sheet(fixture: Fixture, team: Team) -> Dict:
    """Record the clean sheet and goals conceded for one side, then rescore.

    Recomputed rather than accumulated: the stat is derived from the final score
    every time, points are recalculated from the whole line, and the affected
    gameweeks are rescored by the engine. That makes the task safe to re-run,
    and correct if the score is later corrected — the previous version added an
    increment behind an "already processed" marker, so a score changed after the
    fact left the clean-sheet points behind for good.

    It also no longer carries its own copy of the captain rules. That copy had
    the same defect as the others: it worked out a role and then added the
    undoubled points.
    """
    conceded = (
        fixture.away_team_score
        if team == fixture.home_team
        else fixture.home_team_score
    ) or 0

    performances = PlayerPerformance.objects.filter(
        fixture=fixture, gameweek=fixture.gameweek, player__team=team
    ).select_related("player")

    updated_players = []
    errors = []

    with transaction.atomic():
        for performance in performances:
            player = performance.player
            try:
                before = performance.fantasy_points
                kept = (
                    1
                    if conceded == 0
                    and performance.minutes_played >= scoring.CLEAN_SHEET_MIN_MINUTES
                    else 0
                )

                changed = []
                if performance.clean_sheets != kept:
                    performance.clean_sheets = kept
                    changed.append("clean_sheets")
                if performance.goals_conceded != conceded:
                    performance.goals_conceded = conceded
                    changed.append("goals_conceded")

                points = scoring.score_performance(performance)
                if performance.fantasy_points != points:
                    performance.fantasy_points = points
                    changed.append("fantasy_points")

                if changed:
                    performance.save(update_fields=changed + ["updated_at"])
                    updated_players.append(
                        {
                            "player_name": player.name,
                            "position": player.position,
                            "team": team.name,
                            "clean_sheet": bool(kept),
                            "goals_conceded": conceded,
                            "old_points": before,
                            "new_points": performance.fantasy_points,
                        }
                    )
            except Exception as exc:  # noqa: BLE001 - one player must not stop the rest
                logger.error(
                    "Error processing clean sheet for %s: %s",
                    player.name,
                    exc,
                    exc_info=True,
                )
                errors.append({"player_name": player.name, "error": str(exc)})

    # One rescore per affected team, after every performance is settled.
    if updated_players and fixture.gameweek:
        scoring_engine.recalculate_gameweek(fixture.gameweek)

    logger.info(
        "Clean sheet processing for %s: %d players updated, %d errors",
        team.name,
        len(updated_players),
        len(errors),
    )

    return {
        "team": team.name,
        "updated_count": len(updated_players),
        "error_count": len(errors),
        "updated_players": updated_players,
        "errors": errors,
    }


def trigger_clean_sheet_processing():
    """
    Utility function to manually trigger clean sheet processing for all completed fixtures
    in the active gameweek (useful for testing or fixing missing clean sheets).
    """
    from apps.kpl.models import Gameweek

    try:
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        if not active_gameweek:
            logger.info("No active gameweek found")
            return {"success": False, "message": "No active gameweek"}

        completed_fixtures = Fixture.objects.filter(
            gameweek=active_gameweek, status="completed"
        )

        logger.info(
            f"Processing clean sheets for {completed_fixtures.count()} completed fixtures"
        )

        results = []
        for fixture in completed_fixtures:
            result = process_clean_sheets_on_completion(fixture.id)
            results.append(
                {
                    "fixture": f"{fixture.home_team.name} vs {fixture.away_team.name}",
                    "result": result,
                }
            )

        return {
            "success": True,
            "gameweek": active_gameweek.number,
            "fixtures_processed": len(results),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error in trigger_clean_sheet_processing: {e}", exc_info=True)
        return {"success": False, "message": str(e)}
