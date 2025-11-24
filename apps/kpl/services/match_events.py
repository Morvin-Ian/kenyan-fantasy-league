import logging
from typing import Dict, List, Optional, Tuple

from django.db import transaction

from apps.kpl.models import Fixture, Team, ProcessedMatchEvent
from apps.fantasy.models import PlayerPerformance, FantasyPlayer, TeamSelection

logger = logging.getLogger(__name__)


class FixtureValidator:
    """Validates that events belong to the correct fixture"""
    
    @staticmethod
    def validate_player_team_in_fixture(player, fixture: Fixture) -> bool:
        if not player or not fixture:
            return False
            
        is_home_team = player.team.id == fixture.home_team.id
        is_away_team = player.team.id == fixture.away_team.id
        
        if not (is_home_team or is_away_team):
            logger.error(
                f"FIXTURE MISMATCH: Player {player.name} (Team: {player.team.name}) "
                f"is NOT in fixture {fixture.id} ({fixture.home_team.name} vs {fixture.away_team.name})"
            )
            return False
        
        side = "home" if is_home_team else "away"
        logger.debug(
            f"FIXTURE VALID: Player {player.name} (Team: {player.team.name}) "
            f"is in fixture as {side} team"
        )
        return True
    
    @staticmethod
    def validate_team_in_fixture(team_id: str, fixture: Fixture) -> bool:
        """
        Ensure team is actually playing in this fixture
        """
        if not team_id or not fixture:
            return False
            
        is_home_team = str(fixture.home_team.id) == str(team_id)
        is_away_team = str(fixture.away_team.id) == str(team_id)
        
        if not (is_home_team or is_away_team):
            logger.error(
                f"FIXTURE MISMATCH: Team ID {team_id} "
                f"is NOT in fixture {fixture.id} ({fixture.home_team.name} vs {fixture.away_team.name})"
            )
            return False
        
        return True
    
    @staticmethod
    def get_fixture_summary(fixture: Fixture) -> str:
        """Get a human-readable fixture summary"""
        return (
            f"Fixture {fixture.id}: {fixture.home_team.name} vs {fixture.away_team.name} "
            f"(GW{fixture.gameweek.number if fixture.gameweek else 'N/A'})"
        )


class FantasyPointsCalculator:
    @staticmethod
    def calculate_full(performance, is_captain=False):
        """Calculate full points from scratch"""
        position = performance.player.position
        points = 0

        if performance.minutes_played > 0:
            points += 1
        if performance.minutes_played >= 60:
            points += 1

        if position == "GKP":
            points += performance.goals_scored * 6
        elif position == "DEF":
            points += performance.goals_scored * 6
        elif position == "MID":
            points += performance.goals_scored * 5
        else:  # FWD
            points += performance.goals_scored * 4

        points += performance.assists * 3

        if position in ["GKP", "DEF"]:
            points += performance.clean_sheets * 4
        elif position == "MID":
            points += performance.clean_sheets * 1

        if position == "GKP":
            points += performance.saves // 3

        points += performance.penalties_saved * 5
        points -= performance.penalties_missed * 2

        points -= performance.own_goals * 2

        points -= performance.yellow_cards * 1
        points -= performance.red_cards * 3

        if is_captain:
            return points * 2
        return points

    @staticmethod
    def calculate_incremental(new_performance, old_values, is_captain=False):
        position = new_performance.player.position
        points = 0

        old_minutes = old_values["minutes_played"]
        new_minutes = new_performance.minutes_played

        if new_minutes != old_minutes:
            if old_minutes == 0 and new_minutes > 0:
                points += 1  # Appearance point
            if old_minutes < 60 and new_minutes >= 60:
                points += 1  # 60+ minutes point

        goals_diff = new_performance.goals_scored - old_values["goals_scored"]
        if goals_diff > 0:
            if position == "GKP":
                points += goals_diff * 6
            elif position == "DEF":
                points += goals_diff * 6
            elif position == "MID":
                points += goals_diff * 5
            else:  # FWD
                points += goals_diff * 4

        assists_diff = new_performance.assists - old_values["assists"]
        if assists_diff > 0:
            points += assists_diff * 3

        clean_sheets_diff = new_performance.clean_sheets - old_values["clean_sheets"]
        if clean_sheets_diff > 0:
            if position in ["GKP", "DEF"]:
                points += clean_sheets_diff * 4
            elif position == "MID":
                points += clean_sheets_diff * 1

        saves_diff = new_performance.saves - old_values["saves"]
        if saves_diff > 0 and position == "GKP":
            points += saves_diff // 3

        penalties_saved_diff = (
            new_performance.penalties_saved - old_values["penalties_saved"]
        )
        if penalties_saved_diff > 0:
            points += penalties_saved_diff * 5

        penalties_missed_diff = (
            new_performance.penalties_missed - old_values["penalties_missed"]
        )
        if penalties_missed_diff > 0:
            points -= penalties_missed_diff * 2

        own_goals_diff = new_performance.own_goals - old_values["own_goals"]
        if own_goals_diff > 0:
            points -= own_goals_diff * 2

        yellow_cards_diff = new_performance.yellow_cards - old_values["yellow_cards"]
        if yellow_cards_diff > 0:
            points -= yellow_cards_diff * 1

        red_cards_diff = new_performance.red_cards - old_values["red_cards"]
        if red_cards_diff > 0:
            points -= red_cards_diff * 3

        if is_captain:
            return points * 2
        return points


class MatchEventService:
    
    @staticmethod
    def _generate_event_key(event_type: str, fixture_id: int, player_id: int, minute: int, extra_data: str = "") -> str:
        """Generate a unique key for an event to prevent duplicates"""
        base_key = f"{event_type}_{fixture_id}_{player_id}_{minute}"
        if extra_data:
            base_key += f"_{extra_data}"
        return base_key
    
    @staticmethod
    def _is_event_processed(fixture: Fixture, event_key: str) -> bool:
        """Check if an event has already been processed"""
        return ProcessedMatchEvent.objects.filter(
            fixture=fixture,
            event_key=event_key
        ).exists()
    
    @staticmethod
    def _mark_event_processed(fixture: Fixture, event_type: str, event_key: str, 
                            player=None, player_in=None, player_out=None, minute=None):
        """Mark an event as processed"""
        ProcessedMatchEvent.objects.create(
            fixture=fixture,
            event_type=event_type,
            event_key=event_key,
            player=player,
            player_in=player_in,
            player_out=player_out,
            minute=minute
        )
    
    @staticmethod
    def _get_captain_status(player, fixture):
        try:
            captain_selections = TeamSelection.objects.filter(
                gameweek=fixture.gameweek, captain__player=player
            )
            return captain_selections.exists()
        except Exception as e:
            logger.error(f"Error checking captain status for {player.name}: {e}")
            return False
        
    @staticmethod
    def _update_fantasy_team_points(player, fixture, incremental_points=None):
        """
        Update fantasy team points with proper captain/vice-captain handling.
        If captain didn't play, vice-captain gets double points.
        
        Args:
            player: The player whose performance changed
            fixture: The fixture
            incremental_points: If provided, use this instead of recalculating from performance
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
                        continue

                    performance = PlayerPerformance.objects.get(
                        player=player, fixture=fixture, gameweek=fixture.gameweek
                    )

                    if incremental_points is not None:
                        base_points = incremental_points
                    else:
                        base_points = performance.fantasy_points

                    points_to_add = base_points
                    role = "starter"

                    if team_selection.captain.player == player:
                        captain_performance = performance
                        
                        if captain_performance.minutes_played > 0:
                            role = "captain"
                        else:
                            role = "captain_no_play"
                            logger.info(f"Captain {player.name} didn't play in {fantasy_player.fantasy_team.name}")

                    elif team_selection.vice_captain.player == player:
                        # This player is the vice-captain
                        # Check if captain played
                        try:
                            captain_performance = PlayerPerformance.objects.get(
                                player=team_selection.captain.player,
                                fixture=fixture,
                                gameweek=fixture.gameweek
                            )
                            
                            if captain_performance.minutes_played == 0:
                                if incremental_points is not None:
                                    points_to_add = base_points * 2
                                else:
                                    points_to_add = base_points * 2
                                
                                role = "vice_captain_active"
                                logger.info(
                                    f"Vice-captain {player.name} gets double points "
                                    f"(captain didn't play) for {fantasy_player.fantasy_team.name}"
                                )
                            else:
                                role = "vice_captain"
                                
                        except PlayerPerformance.DoesNotExist:
                            if incremental_points is not None:
                                points_to_add = base_points * 2
                            else:
                                points_to_add = base_points * 2
                            role = "vice_captain_active"
                            logger.info(
                                f"Vice-captain {player.name} gets double points "
                                f"(captain no performance) for {fantasy_player.fantasy_team.name}"
                            )

                    fantasy_player.total_points += points_to_add
                    fantasy_player.save()

                    fantasy_team = fantasy_player.fantasy_team
                    fantasy_team.total_points += points_to_add
                    fantasy_team.save()

                    logger.debug(
                        f"Updated {fantasy_player.fantasy_team.name}: "
                        f"+{points_to_add} points for {player.name} ({role})"
                    )

                except TeamSelection.DoesNotExist:
                    continue
                except PlayerPerformance.DoesNotExist:
                    continue

        except Exception as e:
            logger.error(f"Error updating fantasy team points for {player.name}: {e}")

    @staticmethod
    def _store_old_values(performance):
        return {
            "minutes_played": performance.minutes_played,
            "goals_scored": performance.goals_scored,
            "assists": performance.assists,
            "clean_sheets": performance.clean_sheets,
            "saves": performance.saves,
            "penalties_saved": performance.penalties_saved,
            "penalties_missed": performance.penalties_missed,
            "own_goals": performance.own_goals,
            "yellow_cards": performance.yellow_cards,
            "red_cards": performance.red_cards,
            "fantasy_points": performance.fantasy_points,
        }

    @staticmethod
    def update_goals(fixture: Fixture, goals_data: List[Dict]) -> Dict:
        from apps.kpl.tasks.fixtures import find_player

        updated_players = []
        errors = []
        
        logger.info(f"Processing {len(goals_data)} goals for {FixtureValidator.get_fixture_summary(fixture)}")

        with transaction.atomic():
            for goal_data in goals_data:
                player_name = goal_data.get("player_name", "").strip()
                team_id = goal_data.get("team_id")
                count = goal_data.get("count", 1)
                minute = goal_data.get("minute", 0)

                if not player_name or not team_id:
                    errors.append({
                        "player_name": player_name,
                        "error": "player_name and team_id are required",
                    })
                    continue

                try:
                    if not FixtureValidator.validate_team_in_fixture(team_id, fixture):
                        errors.append({
                            "player_name": player_name,
                            "error": f"Team {team_id} is not in this fixture",
                            "fixture": FixtureValidator.get_fixture_summary(fixture),
                        })
                        continue
                    
                    team = Team.objects.get(id=team_id)
                    player = find_player(player_name, team_id=team_id, auto_create=True)

                    if not player:
                        errors.append({
                            "player_name": player_name,
                            "error": f"Player not found in team {team.name}",
                        })
                        continue
                    
                    if not FixtureValidator.validate_player_team_in_fixture(player, fixture):
                        errors.append({
                            "player_name": player_name,
                            "error": f"Player {player.name} team {player.team.name} is not in this fixture",
                            "fixture": FixtureValidator.get_fixture_summary(fixture),
                        })
                        continue

                    # Generate unique event key and check if already processed
                    event_key = MatchEventService._generate_event_key(
                        "goal", fixture.id, player.id, minute
                    )
                    
                    if MatchEventService._is_event_processed(fixture, event_key):
                        logger.info(f"Goal already processed for {player.name} at minute {minute}")
                        continue

                    performance, created = PlayerPerformance.objects.get_or_create(
                        player=player,
                        fixture=fixture,
                        gameweek=fixture.gameweek,
                        defaults={
                            "assists": 0,
                            "goals_scored": 0,
                            "minutes_played": 0,
                            "yellow_cards": 0,
                            "red_cards": 0,
                            "clean_sheets": 0,
                            "saves": 0,
                            "own_goals": 0,
                            "penalties_saved": 0,
                            "penalties_missed": 0,
                            "fantasy_points": 0,
                        },
                    )

                    old_values = MatchEventService._store_old_values(performance)
                    old_goals = performance.goals_scored
                    performance.goals_scored += count

                    is_captain = MatchEventService._get_captain_status(player, fixture)

                    if created:
                        performance.fantasy_points = FantasyPointsCalculator.calculate_full(
                            performance, is_captain
                        )
                    else:
                        incremental_points = FantasyPointsCalculator.calculate_incremental(
                            performance, old_values, is_captain
                        )
                        performance.fantasy_points += incremental_points

                    performance.save()
                    
                    # Mark goal as processed
                    MatchEventService._mark_event_processed(
                        fixture, "goal", event_key, player=player, minute=minute
                    )

                    MatchEventService._update_fantasy_team_points(player, fixture)

                    updated_players.append({
                        "player_name": player.name,
                        "team": team.name,
                        "old_goals": old_goals,
                        "new_goals": performance.goals_scored,
                        "old_points": old_values["fantasy_points"],
                        "new_points": performance.fantasy_points,
                        "is_captain": is_captain,
                        "points_multiplier": 2 if is_captain else 1,
                        "created": created,
                    })

                    logger.info(f"Updated goal for {player.name}: {old_goals} -> {performance.goals_scored}")

                except Team.DoesNotExist:
                    errors.append({
                        "player_name": player_name,
                        "error": f"Team with id {team_id} not found",
                    })
                except Exception as e:
                    errors.append({"player_name": player_name, "error": str(e)})

        logger.info(f"Goals update completed: {len(updated_players)} updated, {len(errors)} errors")
        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def update_assists(fixture: Fixture, assists_data: List[Dict]) -> Dict:
        from apps.kpl.tasks.fixtures import find_player

        updated_players = []
        errors = []
        
        logger.info(f"Processing {len(assists_data)} assists for {FixtureValidator.get_fixture_summary(fixture)}")

        with transaction.atomic():
            for assist_data in assists_data:
                player_name = assist_data.get("player_name", "").strip()
                team_id = assist_data.get("team_id")
                count = assist_data.get("count", 1)
                minute = assist_data.get("minute", 0)

                if not player_name or not team_id:
                    errors.append({
                        "player_name": player_name,
                        "error": "player_name and team_id are required",
                    })
                    continue

                try:
                    if not FixtureValidator.validate_team_in_fixture(team_id, fixture):
                        errors.append({
                            "player_name": player_name,
                            "error": f"Team {team_id} is not in this fixture",
                            "fixture": FixtureValidator.get_fixture_summary(fixture),
                        })
                        continue
                    
                    team = Team.objects.get(id=team_id)
                    player = find_player(player_name, team_id=team_id, auto_create=True)

                    if not player:
                        errors.append({
                            "player_name": player_name,
                            "error": f"Player not found in team {team.name}",
                        })
                        continue
                    
                    if not FixtureValidator.validate_player_team_in_fixture(player, fixture):
                        errors.append({
                            "player_name": player_name,
                            "error": f"Player {player.name} team {player.team.name} is not in this fixture",
                            "fixture": FixtureValidator.get_fixture_summary(fixture),
                        })
                        continue

                    event_key = MatchEventService._generate_event_key(
                        "assist", fixture.id, player.id, minute
                    )
                    
                    if MatchEventService._is_event_processed(fixture, event_key):
                        logger.info(f"Assist already processed for {player.name} at minute {minute}")
                        continue

                    performance, created = PlayerPerformance.objects.get_or_create(
                        player=player,
                        fixture=fixture,
                        gameweek=fixture.gameweek,
                        defaults={
                            "assists": 0,
                            "goals_scored": 0,
                            "minutes_played": 0,
                            "yellow_cards": 0,
                            "red_cards": 0,
                            "clean_sheets": 0,
                            "saves": 0,
                            "own_goals": 0,
                            "penalties_saved": 0,
                            "penalties_missed": 0,
                            "fantasy_points": 0,
                        },
                    )

                    old_values = MatchEventService._store_old_values(performance)
                    old_assists = performance.assists
                    performance.assists += count

                    is_captain = MatchEventService._get_captain_status(player, fixture)

                    if created:
                        performance.fantasy_points = FantasyPointsCalculator.calculate_full(
                            performance, is_captain
                        )
                    else:
                        incremental_points = FantasyPointsCalculator.calculate_incremental(
                            performance, old_values, is_captain
                        )
                        performance.fantasy_points += incremental_points

                    performance.save()
                    
                    MatchEventService._mark_event_processed(
                        fixture, "assist", event_key, player=player, minute=minute
                    )

                    MatchEventService._update_fantasy_team_points(player, fixture)

                    updated_players.append({
                        "player_name": player.name,
                        "team": team.name,
                        "old_assists": old_assists,
                        "new_assists": performance.assists,
                        "old_points": old_values["fantasy_points"],
                        "new_points": performance.fantasy_points,
                        "is_captain": is_captain,
                        "points_multiplier": 2 if is_captain else 1,
                        "created": created,
                    })

                    logger.info(f"Updated assist for {player.name}: {old_assists} -> {performance.assists}")

                except Team.DoesNotExist:
                    errors.append({
                        "player_name": player_name,
                        "error": f"Team with id {team_id} not found",
                    })
                except Exception as e:
                    errors.append({"player_name": player_name, "error": str(e)})

        logger.info(f"Assists update completed: {len(updated_players)} updated, {len(errors)} errors")
        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def update_cards(fixture: Fixture, yellow_cards: List[Dict], red_cards: List[Dict]) -> Dict:
        updated_players = []
        errors = []
        
        logger.info(f"Processing cards for {FixtureValidator.get_fixture_summary(fixture)}")

        with transaction.atomic():
            # Process yellow cards
            for card_data in yellow_cards:
                result = MatchEventService._process_card(
                    fixture, card_data, "yellow_cards", "yellow"
                )
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

            # Process red cards
            for card_data in red_cards:
                result = MatchEventService._process_card(
                    fixture, card_data, "red_cards", "red"
                )
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

        logger.info(f"Cards update completed: {len(updated_players)} updated, {len(errors)} errors")
        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def _process_card(fixture, card_data, field_name, card_type):
        from apps.kpl.tasks.fixtures import find_player

        player_name = card_data.get("player_name", "").strip()
        team_id = card_data.get("team_id")
        count = card_data.get("count", 1)
        minute = card_data.get("minute", 0)

        if not player_name or not team_id:
            return {
                "success": False,
                "error": {
                    "player_name": player_name,
                    "error": "player_name and team_id are required",
                },
            }

        try:
            if not FixtureValidator.validate_team_in_fixture(team_id, fixture):
                return {
                    "success": False,
                    "error": {
                        "player_name": player_name,
                        "error": f"Team {team_id} is not in this fixture",
                        "fixture": FixtureValidator.get_fixture_summary(fixture),
                    },
                }
            
            team = Team.objects.get(id=team_id)
            player = find_player(player_name, team_id=team_id, auto_create=True)

            if not player:
                return {
                    "success": False,
                    "error": {
                        "player_name": player_name,
                        "error": f"Player not found in team {team.name}",
                    },
                }
            
            if not FixtureValidator.validate_player_team_in_fixture(player, fixture):
                return {
                    "success": False,
                    "error": {
                        "player_name": player_name,
                        "error": f"Player {player.name} team {player.team.name} is not in this fixture",
                        "fixture": FixtureValidator.get_fixture_summary(fixture),
                    },
                }

            event_key = MatchEventService._generate_event_key(
                f"{card_type}_card", fixture.id, player.id, minute
            )
            
            if MatchEventService._is_event_processed(fixture, event_key):
                logger.info(f"{card_type.title()} card already processed for {player.name} at minute {minute}")
                return {
                    "success": True,
                    "data": {
                        "player_name": player.name,
                        "status": "already_processed",
                        "message": f"{card_type.title()} card was already processed"
                    }
                }

            is_captain = MatchEventService._get_captain_status(player, fixture)

            performance, created = PlayerPerformance.objects.get_or_create(
                player=player,
                fixture=fixture,
                gameweek=fixture.gameweek,
                defaults={
                    "assists": 0,
                    "goals_scored": 0,
                    "minutes_played": 0,
                    "yellow_cards": 0,
                    "red_cards": 0,
                    "clean_sheets": 0,
                    "saves": 0,
                    "own_goals": 0,
                    "penalties_saved": 0,
                    "penalties_missed": 0,
                    "fantasy_points": 0,
                },
            )

            old_values = MatchEventService._store_old_values(performance)
            current_value = getattr(performance, field_name, 0)
            old_card_count = current_value
            setattr(performance, field_name, current_value + count)

            if created:
                performance.fantasy_points = FantasyPointsCalculator.calculate_full(
                    performance, is_captain
                )
            else:
                incremental_points = FantasyPointsCalculator.calculate_incremental(
                    performance, old_values, is_captain
                )
                performance.fantasy_points += incremental_points

            performance.save()
            
            MatchEventService._mark_event_processed(
                fixture, f"{card_type}_card", event_key, player=player, minute=minute
            )

            MatchEventService._update_fantasy_team_points(player, fixture)

            return {
                "success": True,
                "data": {
                    "player_name": player.name,
                    "team": team.name,
                    "card_type": card_type,
                    f"old_{field_name}": old_card_count,
                    f"new_{field_name}": getattr(performance, field_name),
                    "old_points": old_values["fantasy_points"],
                    "new_points": performance.fantasy_points,
                    "is_captain": is_captain,
                    "points_multiplier": 2 if is_captain else 1,
                    "created": created,
                },
            }

        except Team.DoesNotExist:
            return {
                "success": False,
                "error": {
                    "player_name": player_name,
                    "error": f"Team with id {team_id} not found",
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": {"player_name": player_name, "error": str(e)},
            }

    @staticmethod
    def update_substitutions(fixture: Fixture, substitutions: List[Dict]) -> Dict:
        from apps.kpl.tasks.fixtures import find_player

        updated_players = []
        errors = []

        with transaction.atomic():
            for sub_data in substitutions:
                player_out_name = sub_data.get("player_out", "").strip()
                player_in_name = sub_data.get("player_in", "").strip()
                team_id = sub_data.get("team_id")
                minute = sub_data.get("minute", 0)

                if not all([player_out_name, player_in_name, team_id]):
                    errors.append({"error": "player_out, player_in, and team_id are required"})
                    continue

                try:
                    team = Team.objects.get(id=team_id)

                    # Process player out
                    player_out = find_player(player_out_name, team_id=team_id, auto_create=True)
                    if player_out:
                        # Generate unique event key for substitution out
                        event_key_out = MatchEventService._generate_event_key(
                            "substitution_out", fixture.id, player_out.id, minute
                        )
                        
                        if not MatchEventService._is_event_processed(fixture, event_key_out):
                            is_captain_out = MatchEventService._get_captain_status(player_out, fixture)

                            perf_out, created_out = PlayerPerformance.objects.get_or_create(
                                player=player_out,
                                fixture=fixture,
                                gameweek=fixture.gameweek,
                                defaults={
                                    "assists": 0,
                                    "goals_scored": 0,
                                    "minutes_played": 0,
                                    "yellow_cards": 0,
                                    "red_cards": 0,
                                    "clean_sheets": 0,
                                    "saves": 0,
                                    "own_goals": 0,
                                    "penalties_saved": 0,
                                    "penalties_missed": 0,
                                    "fantasy_points": 0,
                                },
                            )

                            old_values_out = MatchEventService._store_old_values(perf_out)
                            old_minutes_out = perf_out.minutes_played
                            perf_out.minutes_played = minute

                            if created_out:
                                perf_out.fantasy_points = FantasyPointsCalculator.calculate_full(
                                    perf_out, is_captain_out
                                )
                            else:
                                incremental_points = FantasyPointsCalculator.calculate_incremental(
                                    perf_out, old_values_out, is_captain_out
                                )
                                perf_out.fantasy_points += incremental_points

                            perf_out.save()
                            
                            # Mark substitution out as processed
                            MatchEventService._mark_event_processed(
                                fixture, "substitution_out", event_key_out, 
                                player=player_out, minute=minute
                            )

                            MatchEventService._update_fantasy_team_points(player_out, fixture)

                            updated_players.append({
                                "player_name": player_out.name,
                                "team": team.name,
                                "status": "substituted_out",
                                "old_minutes": old_minutes_out,
                                "new_minutes": perf_out.minutes_played,
                                "old_points": old_values_out["fantasy_points"],
                                "new_points": perf_out.fantasy_points,
                                "is_captain": is_captain_out,
                                "points_multiplier": 2 if is_captain_out else 1,
                                "created": created_out,
                            })

                            logger.info(f"Updated substitution out for {player_out.name}: minutes {old_minutes_out} -> {perf_out.minutes_played}")
                        else:
                            logger.info(f"Substitution out already processed for {player_out.name} at minute {minute}")
                    else:
                        errors.append({
                            "player_name": player_out_name,
                            "error": f"Player not found in team {team.name}",
                        })

                    # Process player in
                    player_in = find_player(player_in_name, team_id=team_id, auto_create=True)
                    if player_in:
                        # Generate unique event key for substitution in
                        event_key_in = MatchEventService._generate_event_key(
                            "substitution_in", fixture.id, player_in.id, minute
                        )
                        
                        if not MatchEventService._is_event_processed(fixture, event_key_in):
                            is_captain_in = MatchEventService._get_captain_status(player_in, fixture)
                            minutes_in = 90 - minute

                            perf_in, created_in = PlayerPerformance.objects.get_or_create(
                                player=player_in,
                                fixture=fixture,
                                gameweek=fixture.gameweek,
                                defaults={
                                    "assists": 0,
                                    "goals_scored": 0,
                                    "minutes_played": 0,
                                    "yellow_cards": 0,
                                    "red_cards": 0,
                                    "clean_sheets": 0,
                                    "saves": 0,
                                    "own_goals": 0,
                                    "penalties_saved": 0,
                                    "penalties_missed": 0,
                                    "fantasy_points": 0,
                                },
                            )

                            old_values_in = MatchEventService._store_old_values(perf_in)
                            old_minutes_in = perf_in.minutes_played
                            perf_in.minutes_played = minutes_in

                            if created_in:
                                perf_in.fantasy_points = FantasyPointsCalculator.calculate_full(
                                    perf_in, is_captain_in
                                )
                            else:
                                incremental_points = FantasyPointsCalculator.calculate_incremental(
                                    perf_in, old_values_in, is_captain_in
                                )
                                perf_in.fantasy_points += incremental_points

                            perf_in.save()
                            
                            # Mark substitution in as processed
                            MatchEventService._mark_event_processed(
                                fixture, "substitution_in", event_key_in, 
                                player=player_in, minute=minute
                            )

                            MatchEventService._update_fantasy_team_points(player_in, fixture)

                            updated_players.append({
                                "player_name": player_in.name,
                                "team": team.name,
                                "status": "substituted_in",
                                "old_minutes": old_minutes_in,
                                "new_minutes": perf_in.minutes_played,
                                "old_points": old_values_in["fantasy_points"],
                                "new_points": perf_in.fantasy_points,
                                "is_captain": is_captain_in,
                                "points_multiplier": 2 if is_captain_in else 1,
                                "created": created_in,
                            })

                            logger.info(f"Updated substitution in for {player_in.name}: minutes {old_minutes_in} -> {perf_in.minutes_played}")
                        else:
                            logger.info(f"Substitution in already processed for {player_in.name} at minute {minute}")
                    else:
                        errors.append({
                            "player_name": player_in_name,
                            "error": f"Player not found in team {team.name}",
                        })

                except Team.DoesNotExist:
                    errors.append({"error": f"Team with id {team_id} not found"})
                except Exception as e:
                    errors.append({"error": str(e)})

        logger.info(f"Substitutions update completed: {len(updated_players)} updated, {len(errors)} errors")
        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def update_clean_sheets(fixture: Fixture, clean_sheet_data: List[Dict]) -> Dict:
        from apps.kpl.tasks.fixtures import find_player

        updated_players = []
        errors = []

        with transaction.atomic():
            for cs_data in clean_sheet_data:
                player_name = cs_data.get("player_name", "").strip()
                team_id = cs_data.get("team_id")
                count = cs_data.get("count", 1)

                if not player_name or not team_id:
                    errors.append({
                        "player_name": player_name,
                        "error": "player_name and team_id are required",
                    })
                    continue

                try:
                    team = Team.objects.get(id=team_id)
                    player = find_player(player_name)

                    if not player:
                        errors.append({
                            "player_name": player_name,
                            "error": f"Player not found in team {team.name}",
                        })
                        continue

                    # For clean sheets, we don't use minute-based tracking since it's a match-level stat
                    # But we still track to prevent multiple updates
                    event_key = MatchEventService._generate_event_key(
                        "clean_sheet", fixture.id, player.id, 0, f"team_{team_id}"
                    )
                    
                    if MatchEventService._is_event_processed(fixture, event_key):
                        logger.info(f"Clean sheet already processed for {player.name}")
                        continue

                    performance, created = PlayerPerformance.objects.get_or_create(
                        player=player,
                        fixture=fixture,
                        gameweek=fixture.gameweek,
                        defaults={
                            "assists": 0,
                            "goals_scored": 0,
                            "minutes_played": 0,
                            "yellow_cards": 0,
                            "red_cards": 0,
                            "clean_sheets": 0,
                            "saves": 0,
                            "own_goals": 0,
                            "penalties_saved": 0,
                            "penalties_missed": 0,
                            "fantasy_points": 0,
                        },
                    )

                    old_values = MatchEventService._store_old_values(performance)
                    old_clean_sheets = performance.clean_sheets
                    performance.clean_sheets += count

                    is_captain = MatchEventService._get_captain_status(player, fixture)

                    if created:
                        performance.fantasy_points = FantasyPointsCalculator.calculate_full(
                            performance, is_captain
                        )
                    else:
                        incremental_points = FantasyPointsCalculator.calculate_incremental(
                            performance, old_values, is_captain
                        )
                        performance.fantasy_points += incremental_points

                    performance.save()
                    
                    # Mark clean sheet as processed
                    MatchEventService._mark_event_processed(
                        fixture, "clean_sheet", event_key, player=player
                    )

                    MatchEventService._update_fantasy_team_points(player, fixture)

                    updated_players.append({
                        "player_name": player.name,
                        "team": team.name,
                        "old_clean_sheets": old_clean_sheets,
                        "new_clean_sheets": performance.clean_sheets,
                        "old_points": old_values["fantasy_points"],
                        "new_points": performance.fantasy_points,
                        "is_captain": is_captain,
                        "points_multiplier": 2 if is_captain else 1,
                        "created": created,
                    })

                    logger.info(f"Updated clean sheet for {player.name}: {old_clean_sheets} -> {performance.clean_sheets}")

                except Team.DoesNotExist:
                    errors.append({
                        "player_name": player_name,
                        "error": f"Team with id {team_id} not found",
                    })
                except Exception as e:
                    errors.append({"player_name": player_name, "error": str(e)})

        logger.info(f"Clean sheets update completed: {len(updated_players)} updated, {len(errors)} errors")
        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def update_own_goals(fixture: Fixture, own_goals_data: List[Dict]) -> Dict:
        from apps.kpl.tasks.fixtures import find_player

        updated_players = []
        errors = []

        with transaction.atomic():
            for own_goal_data in own_goals_data:
                player_name = own_goal_data.get("player_name", "").strip()
                team_id = own_goal_data.get("team_id")
                count = own_goal_data.get("count", 1)
                minute = own_goal_data.get("minute", 0)

                if not player_name or not team_id:
                    errors.append({
                        "player_name": player_name,
                        "error_code": "MISSING_REQUIRED_FIELDS",
                        "message": "player_name and team_id are required",
                    })
                    continue

                if count < 0:
                    errors.append({
                        "player_name": player_name,
                        "error_code": "INVALID_COUNT",
                        "message": "count cannot be negative",
                    })
                    continue

                try:
                    team = Team.objects.get(id=team_id)
                    player = find_player(player_name, team_id=team_id)

                    if not player:
                        errors.append({
                            "player_name": player_name,
                            "error_code": "PLAYER_NOT_FOUND",
                            "message": f"Player not found in team {team.name}",
                        })
                        continue

                    # Generate unique event key and check if already processed
                    event_key = MatchEventService._generate_event_key(
                        "own_goal", fixture.id, player.id, minute
                    )
                    
                    if MatchEventService._is_event_processed(fixture, event_key):
                        logger.info(f"Own goal already processed for {player.name} at minute {minute}")
                        continue

                    performance, created = PlayerPerformance.objects.get_or_create(
                        player=player,
                        fixture=fixture,
                        gameweek=fixture.gameweek,
                        defaults={
                            "assists": 0,
                            "goals_scored": 0,
                            "minutes_played": 0,
                            "yellow_cards": 0,
                            "red_cards": 0,
                            "clean_sheets": 0,
                            "saves": 0,
                            "own_goals": 0,
                            "penalties_saved": 0,
                            "penalties_missed": 0,
                            "fantasy_points": 0,
                        },
                    )

                    old_values = MatchEventService._store_old_values(performance)
                    old_own_goals = performance.own_goals
                    performance.own_goals += count

                    is_captain = MatchEventService._get_captain_status(player, fixture)

                    if created:
                        performance.fantasy_points = FantasyPointsCalculator.calculate_full(
                            performance, is_captain
                        )
                    else:
                        incremental_points = FantasyPointsCalculator.calculate_incremental(
                            performance, old_values, is_captain
                        )
                        performance.fantasy_points += incremental_points

                    performance.save()
                    
                    # Mark own goal as processed
                    MatchEventService._mark_event_processed(
                        fixture, "own_goal", event_key, player=player, minute=minute
                    )

                    MatchEventService._update_fantasy_team_points(player, fixture)

                    updated_players.append({
                        "player_name": player.name,
                        "team": team.name,
                        "old_own_goals": old_own_goals,
                        "new_own_goals": performance.own_goals,
                        "old_points": old_values["fantasy_points"],
                        "new_points": performance.fantasy_points,
                        "points_deducted": abs(incremental_points) if not created else abs(performance.fantasy_points - old_values["fantasy_points"]),
                        "is_captain": is_captain,
                        "points_multiplier": 2 if is_captain else 1,
                        "created": created,
                    })

                    logger.info(f"Updated own goal for {player.name}: {old_own_goals} -> {performance.own_goals}")

                except Team.DoesNotExist:
                    errors.append({
                        "player_name": player_name,
                        "error_code": "TEAM_NOT_FOUND",
                        "message": f"Team with id {team_id} not found",
                    })
                except Exception as e:
                    logger.error(f"Error updating own goals for {player_name}: {e}")
                    errors.append({
                        "player_name": player_name,
                        "error_code": "UNEXPECTED_ERROR",
                        "message": str(e),
                    })

        logger.info(f"Own goals update completed: {len(updated_players)} updated, {len(errors)} errors")
        return {
            "updated": len(updated_players),
            "failed": len(errors),
            "players": updated_players,
            "errors": errors,
        }

    @staticmethod
    def cleanup_fixture_events(fixture_id: int):
        """Clean up all processed events for a fixture (useful for testing/resets)"""
        try:
            deleted_count, _ = ProcessedMatchEvent.objects.filter(fixture_id=fixture_id).delete()
            logger.info(f"Cleaned up {deleted_count} processed events for fixture {fixture_id}")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up events for fixture {fixture_id}: {e}")
            return 0

    @staticmethod
    def get_processed_events_count(fixture: Fixture) -> Dict:
        """Get count of processed events by type for a fixture"""
        from django.db.models import Count
        
        counts = ProcessedMatchEvent.objects.filter(fixture=fixture).values('event_type').annotate(
            count=Count('id')
        )
        
        result = {item['event_type']: item['count'] for item in counts}
        logger.info(f"Processed events for fixture {fixture.id}: {result}")
        return result