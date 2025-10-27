import logging
from typing import Dict, List

from celery import shared_task
from django.db import transaction
from django.db.models import Q

from apps.kpl.models import Fixture, Team
from apps.fantasy.models import PlayerPerformance, FantasyPlayer, TeamSelection
from apps.kpl.services.match_events import (
    MatchEventService,
    FantasyPointsCalculator,
    FixtureValidator
)

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
            logger.warning(f"Fixture {fixture_id} is not completed. Status: {fixture.status}")
            return {"success": False, "message": "Fixture not completed"}
        
        logger.info(f"Processing clean sheets for {FixtureValidator.get_fixture_summary(fixture)}")
        
        clean_sheet_teams = []
        
        if fixture.away_team_score == 0:
            clean_sheet_teams.append({
                "team": fixture.home_team,
                "side": "home"
            })
            logger.info(f"{fixture.home_team.name} kept a clean sheet (0 goals conceded)")
        
        if fixture.home_team_score == 0:
            clean_sheet_teams.append({
                "team": fixture.away_team,
                "side": "away"
            })
            logger.info(f"{fixture.away_team.name} kept a clean sheet (0 goals conceded)")
        
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
            "details": results
        }
        
    except Fixture.DoesNotExist:
        logger.error(f"Fixture {fixture_id} not found")
        return {"success": False, "message": f"Fixture {fixture_id} not found"}
    except Exception as e:
        logger.error(f"Error processing clean sheets for fixture {fixture_id}: {e}", exc_info=True)
        return {"success": False, "message": str(e)}


def _process_team_clean_sheet(fixture: Fixture, team: Team) -> Dict:
    """
    Process clean sheet for a specific team.
    Awards points to GKP, DEF, and MID who played.
    """
    updated_players = []
    errors = []
    
    # Get all performances for this team in this fixture
    # Only players who actually played (minutes > 0)
    performances = PlayerPerformance.objects.filter(
        fixture=fixture,
        gameweek=fixture.gameweek,
        player__team=team,
        minutes_played__gt=0
    ).select_related('player')
    
    logger.info(f"Found {performances.count()} players from {team.name} who played")
    
    with transaction.atomic():
        for performance in performances:
            player = performance.player
            position = player.position
            
            # Only GKP, DEF, and MID get clean sheet points
            if position not in ["GKP", "DEF", "MID"]:
                logger.debug(f"Skipping {player.name} ({position}) - not eligible for clean sheet")
                continue
            
            # Check if clean sheet already processed
            event_key = MatchEventService._generate_event_key(
                "clean_sheet", fixture.id, player.id, 0, f"team_{team.id}"
            )
            
            if MatchEventService._is_event_processed(fixture, event_key):
                logger.info(f"Clean sheet already processed for {player.name}")
                continue
            
            try:
                # Store old values
                old_values = MatchEventService._store_old_values(performance)
                old_clean_sheets = performance.clean_sheets
                old_points = performance.fantasy_points
                
                performance.clean_sheets += 1
                
                is_captain = MatchEventService._get_captain_status(player, fixture)
                
                incremental_points = FantasyPointsCalculator.calculate_incremental(
                    performance, old_values, is_captain
                )
                performance.fantasy_points += incremental_points
                
                performance.save()
                
                # Mark event as processed
                MatchEventService._mark_event_processed(
                    fixture, "clean_sheet", event_key, player=player
                )
                
                _update_fantasy_teams_with_captain_logic(player, fixture, incremental_points)
                
                updated_players.append({
                    "player_name": player.name,
                    "position": position,
                    "team": team.name,
                    "old_clean_sheets": old_clean_sheets,
                    "new_clean_sheets": performance.clean_sheets,
                    "old_points": old_points,
                    "new_points": performance.fantasy_points,
                    "points_added": incremental_points,
                    "is_captain": is_captain,
                })
                
                logger.info(
                    f"Clean sheet awarded to {player.name} ({position}): "
                    f"{old_points} → {performance.fantasy_points} points "
                    f"{'(CAPTAIN - 2x)' if is_captain else ''}"
                )
                
            except Exception as e:
                logger.error(f"Error processing clean sheet for {player.name}: {e}", exc_info=True)
                errors.append({
                    "player_name": player.name,
                    "error": str(e)
                })
    
    logger.info(
        f"Clean sheet processing for {team.name}: "
        f"{len(updated_players)} players updated, {len(errors)} errors"
    )
    
    return {
        "team": team.name,
        "updated_count": len(updated_players),
        "error_count": len(errors),
        "updated_players": updated_players,
        "errors": errors
    }


def _update_fantasy_teams_with_captain_logic(player, fixture, base_incremental_points):
    """
    Update fantasy team points with proper captain/vice-captain handling.
    If captain didn't play, vice-captain gets double points.
    """
    try:
        fantasy_players = FantasyPlayer.objects.filter(player=player)
        
        for fantasy_player in fantasy_players:
            try:
                team_selection = TeamSelection.objects.get(
                    fantasy_team=fantasy_player.fantasy_team,
                    gameweek=fixture.gameweek,
                    is_finalized=True,
                )
                
                is_starter = fantasy_player in team_selection.starters.all()
                
                if not is_starter:
                    logger.debug(f"{player.name} not in starting lineup for {fantasy_player.fantasy_team.name}")
                    continue
                
                points_to_add = base_incremental_points
                role = "starter"
                
                if team_selection.captain.player == player:
                    captain_performance = PlayerPerformance.objects.get(
                        player=team_selection.captain.player,
                        fixture=fixture,
                        gameweek=fixture.gameweek
                    )
                    
                    if captain_performance.minutes_played > 0:
                        role = "captain"
                    else:
                        logger.info(f"Captain {team_selection.captain.player.name} didn't play")
                        
                elif team_selection.vice_captain.player == player:
                    captain_performance = PlayerPerformance.objects.filter(
                        player=team_selection.captain.player,
                        fixture=fixture,
                        gameweek=fixture.gameweek
                    ).first()
                    
                    if not captain_performance or captain_performance.minutes_played == 0:
                        points_to_add = base_incremental_points * 2
                        role = "vice_captain_active"
                        logger.info(
                            f"Vice-captain {player.name} gets double points "
                            f"(captain didn't play) for {fantasy_player.fantasy_team.name}"
                        )
                    else:
                        role = "vice_captain"
                
                fantasy_player.total_points += points_to_add
                fantasy_player.save()
                
                fantasy_team = fantasy_player.fantasy_team
                fantasy_team.total_points += points_to_add
                fantasy_team.save()
                
                logger.info(
                    f"Updated {fantasy_player.fantasy_team.name}: "
                    f"+{points_to_add} points for {player.name} ({role})"
                )
                
            except TeamSelection.DoesNotExist:
                logger.debug(f"No finalized team selection for {fantasy_player.fantasy_team.name} in GW{fixture.gameweek.number}")
                continue
            except PlayerPerformance.DoesNotExist:
                logger.warning(f"No performance record for {player.name} in fixture {fixture.id}")
                continue
            except Exception as e:
                logger.error(
                    f"Error updating fantasy team {fantasy_player.fantasy_team.name} "
                    f"for player {player.name}: {e}",
                    exc_info=True
                )
                
    except Exception as e:
        logger.error(f"Error in captain/vice-captain logic for {player.name}: {e}", exc_info=True)


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
            gameweek=active_gameweek,
            status="completed"
        )
        
        logger.info(f"Processing clean sheets for {completed_fixtures.count()} completed fixtures")
        
        results = []
        for fixture in completed_fixtures:
            result = process_clean_sheets_on_completion(fixture.id)
            results.append({
                "fixture": f"{fixture.home_team.name} vs {fixture.away_team.name}",
                "result": result
            })
        
        return {
            "success": True,
            "gameweek": active_gameweek.number,
            "fixtures_processed": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in trigger_clean_sheet_processing: {e}", exc_info=True)
        return {"success": False, "message": str(e)}