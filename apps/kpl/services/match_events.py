import logging
from typing import Dict, List

from django.db import transaction

from apps.kpl.models import (
    Fixture,
    Team,
)
from apps.fantasy.models import PlayerPerformance
from apps.kpl.tasks.fixtures import find_player

logger = logging.getLogger(__name__)


class MatchEventService:
    """Service for handling match events and player performance updates"""

    @staticmethod
    def update_assists(fixture: Fixture, assists_data: List[Dict]) -> Dict:
        """Update assists for players in a fixture"""
        updated_players = []
        errors = []

        with transaction.atomic():
            for assist_data in assists_data:
                player_name = assist_data.get("player_name", "").strip()
                team_id = assist_data.get("team_id")
                count = assist_data.get("count", 1)

                if not player_name or not team_id:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error": "player_name and team_id are required",
                        }
                    )
                    continue

                try:
                    team = Team.objects.get(id=team_id)
                    player = find_player(player_name)

                    if not player:
                        errors.append(
                            {
                                "player_name": player_name,
                                "error": f"Player not found in team {team.name}",
                            }
                        )
                        continue

                    performance, created = PlayerPerformance.objects.get_or_create(
                        player=player,
                        fixture=fixture,
                        gameweek=fixture.gameweek,
                        defaults={"assists": count},
                    )

                    if not created:
                        performance.assists += count

                    performance.fantasy_points = FantasyPointsCalculator.calculate(
                        performance
                    )
                    performance.save()

                    updated_players.append(
                        {
                            "player_name": player.name,
                            "team": team.name,
                            "assists": performance.assists,
                            "fantasy_points": performance.fantasy_points,
                        }
                    )

                except Team.DoesNotExist:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error": f"Team with id {team_id} not found",
                        }
                    )
                except Exception as e:
                    errors.append({"player_name": player_name, "error": str(e)})

        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def update_cards(
        fixture: Fixture, yellow_cards: List[Dict], red_cards: List[Dict]
    ) -> Dict:
        """Update yellow and red cards for players"""
        updated_players = []
        errors = []

        with transaction.atomic():
            for card_data in yellow_cards:
                result = MatchEventService._process_card(
                    fixture, card_data, "yellow_cards", "yellow"
                )
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

            for card_data in red_cards:
                result = MatchEventService._process_card(
                    fixture, card_data, "red_cards", "red"
                )
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def update_substitutions(fixture: Fixture, substitutions: List[Dict]) -> Dict:
        """Update substitutions and adjust minutes played"""
        updated_players = []
        errors = []

        with transaction.atomic():
            for sub_data in substitutions:
                player_out_name = sub_data.get("player_out", "").strip()
                player_in_name = sub_data.get("player_in", "").strip()
                team_id = sub_data.get("team_id")
                minute = sub_data.get("minute", 0)

                if not all([player_out_name, player_in_name, team_id]):
                    errors.append(
                        {"error": "player_out, player_in, and team_id are required"}
                    )
                    continue

                try:
                    team = Team.objects.get(id=team_id)
                    player_out = find_player(player_out_name)

                    if player_out:
                        perf_out, _ = PlayerPerformance.objects.get_or_create(
                            player=player_out,
                            fixture=fixture,
                            gameweek=fixture.gameweek,
                            defaults={"minutes_played": minute},
                        )
                        perf_out.minutes_played = minute
                        perf_out.fantasy_points = FantasyPointsCalculator.calculate(
                            perf_out
                        )
                        perf_out.save()

                        updated_players.append(
                            {
                                "player_name": player_out.name,
                                "team": team.name,
                                "status": "substituted_out",
                                "minutes_played": minute,
                                "fantasy_points": perf_out.fantasy_points,
                            }
                        )
                    else:
                        errors.append(
                            {
                                "player_name": player_out_name,
                                "error": f"Player not found in team {team.name}",
                            }
                        )

                    player_in = find_player(player_in_name)

                    if player_in:
                        minutes_in = 90 - minute
                        perf_in, _ = PlayerPerformance.objects.get_or_create(
                            player=player_in,
                            fixture=fixture,
                            gameweek=fixture.gameweek,
                            defaults={"minutes_played": minutes_in},
                        )
                        perf_in.minutes_played = minutes_in
                        perf_in.fantasy_points = FantasyPointsCalculator.calculate(
                            perf_in
                        )
                        perf_in.save()

                        updated_players.append(
                            {
                                "player_name": player_in.name,
                                "team": team.name,
                                "status": "substituted_in",
                                "minutes_played": minutes_in,
                                "fantasy_points": perf_in.fantasy_points,
                            }
                        )
                    else:
                        errors.append(
                            {
                                "player_name": player_in_name,
                                "error": f"Player not found in team {team.name}",
                            }
                        )

                except Team.DoesNotExist:
                    errors.append({"error": f"Team with id {team_id} not found"})
                except Exception as e:
                    errors.append({"error": str(e)})

        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def update_minutes(fixture: Fixture, minutes_data: List[Dict]) -> Dict:
        """Update minutes played for players"""
        updated_players = []
        errors = []

        with transaction.atomic():
            for minute_data in minutes_data:
                player_name = minute_data.get("player_name", "").strip()
                team_id = minute_data.get("team_id")
                minutes_played = minute_data.get("minutes_played", 0)

                if not player_name or not team_id:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error": "player_name and team_id are required",
                        }
                    )
                    continue

                try:
                    team = Team.objects.get(id=team_id)
                    player = find_player(player_name)

                    if not player:
                        errors.append(
                            {
                                "player_name": player_name,
                                "error": f"Player not found in team {team.name}",
                            }
                        )
                        continue

                    performance, created = PlayerPerformance.objects.get_or_create(
                        player=player,
                        fixture=fixture,
                        gameweek=fixture.gameweek,
                        defaults={"minutes_played": minutes_played},
                    )

                    if not created:
                        performance._old_minutes_played = performance.minutes_played
                        performance.minutes_played = minutes_played

                        incremental_points = FantasyPointsCalculator.calculate(
                            performance, is_incremental=True
                        )
                        performance.fantasy_points += incremental_points
                        performance.save()

                        points_added = incremental_points
                    else:
                        performance.fantasy_points = FantasyPointsCalculator.calculate(
                            performance
                        )
                        performance.save()
                        points_added = performance.fantasy_points

                    updated_players.append(
                        {
                            "player_name": player.name,
                            "team": team.name,
                            "minutes_played": minutes_played,
                            "fantasy_points": performance.fantasy_points,
                            "points_added": points_added,
                        }
                    )

                except Team.DoesNotExist:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error": f"Team with id {team_id} not found",
                        }
                    )
                except Exception as e:
                    errors.append({"player_name": player_name, "error": str(e)})

        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def update_goalkeeper_stats(
        fixture: Fixture,
        saves: List[Dict],
        penalties_saved: List[Dict],
        penalties_missed: List[Dict],
    ) -> Dict:
        """Update goalkeeper statistics"""
        updated_players = []
        errors = []

        with transaction.atomic():
            for stat_data in saves:
                result = MatchEventService._process_stat(fixture, stat_data, "saves")
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

            for stat_data in penalties_saved:
                result = MatchEventService._process_stat(
                    fixture, stat_data, "penalties_saved"
                )
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

            for stat_data in penalties_missed:
                result = MatchEventService._process_stat(
                    fixture, stat_data, "penalties_missed"
                )
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

        return {"updated_players": updated_players, "errors": errors}

    @staticmethod
    def _process_card(fixture, card_data, field_name, card_type):
        """Process a card event for a player"""
        player_name = card_data.get("player_name", "").strip()
        team_id = card_data.get("team_id")
        count = card_data.get("count", 1)

        if not player_name or not team_id:
            return {
                "success": False,
                "error": {
                    "player_name": player_name,
                    "error": "player_name and team_id are required",
                },
            }

        try:
            team = Team.objects.get(id=team_id)
            player = find_player(player_name)

            if not player:
                return {
                    "success": False,
                    "error": {
                        "player_name": player_name,
                        "error": f"Player not found in team {team.name}",
                    },
                }

            performance, created = PlayerPerformance.objects.get_or_create(
                player=player,
                fixture=fixture,
                gameweek=fixture.gameweek,
            )

            if not created:
                setattr(
                    performance, f"_old_{field_name}", getattr(performance, field_name)
                )

            current_value = getattr(performance, field_name, 0)
            setattr(performance, field_name, current_value + count)

            if created:
                performance.fantasy_points = FantasyPointsCalculator.calculate(
                    performance
                )
            else:
                incremental_points = FantasyPointsCalculator.calculate(
                    performance, is_incremental=True
                )
                performance.fantasy_points += incremental_points

            performance.save()

            return {
                "success": True,
                "data": {
                    "player_name": player.name,
                    "team": team.name,
                    "card_type": card_type,
                    field_name: getattr(performance, field_name),
                    "fantasy_points": performance.fantasy_points,
                    "points_added": (
                        incremental_points
                        if not created
                        else performance.fantasy_points
                    ),
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
    def _process_stat(fixture, stat_data, field_name):
        """Process a goalkeeper stat for a player"""
        player_name = stat_data.get("player_name", "").strip()
        team_id = stat_data.get("team_id")
        count = stat_data.get("count", 0)

        if not player_name or not team_id:
            return {
                "success": False,
                "error": {
                    "player_name": player_name,
                    "error": "player_name and team_id are required",
                },
            }

        try:
            team = Team.objects.get(id=team_id)
            player = find_player(player_name)
            if not player:
                return {
                    "success": False,
                    "error": {
                        "player_name": player_name,
                        "error": f"Player not found in team {team.name}",
                    },
                }

            performance, created = PlayerPerformance.objects.get_or_create(
                player=player,
                fixture=fixture,
                gameweek=fixture.gameweek,
            )

            if not created:
                setattr(
                    performance, f"_old_{field_name}", getattr(performance, field_name)
                )

            current_value = getattr(performance, field_name, 0)
            setattr(performance, field_name, current_value + count)

            if created:
                performance.fantasy_points = FantasyPointsCalculator.calculate(
                    performance
                )
            else:
                incremental_points = FantasyPointsCalculator.calculate(
                    performance, is_incremental=True
                )
                performance.fantasy_points += incremental_points

            performance.save()

            return {
                "success": True,
                "data": {
                    "player_name": player.name,
                    "team": team.name,
                    "stat_type": field_name,
                    field_name: getattr(performance, field_name),
                    "fantasy_points": performance.fantasy_points,
                    "points_added": (
                        incremental_points
                        if not created
                        else performance.fantasy_points
                    ),
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


class FantasyPointsCalculator:
    """Calculator for fantasy points based on player performance"""

    @staticmethod
    def calculate(performance, is_incremental=False):
        """
        Calculate fantasy points for a player performance

        Args:
            performance: PlayerPerformance instance
            is_incremental: If True, calculate only the difference from previous values
        """
        position = performance.player.position

        if is_incremental:
            return FantasyPointsCalculator._calculate_incremental(performance, position)
        else:
            return FantasyPointsCalculator._calculate_full(performance, position)

    @staticmethod
    def _calculate_incremental(performance, position):
        """Calculate incremental points based on changes"""
        points = 0

        # Minutes played
        old_minutes = getattr(
            performance, "_old_minutes_played", performance.minutes_played
        )
        if performance.minutes_played != old_minutes:
            if old_minutes == 0 and performance.minutes_played > 0:
                points += 1  # Appearance point
            if old_minutes < 60 and performance.minutes_played >= 60:
                points += 1  # 60+ minutes point

        old_values = {
            "goals_scored": getattr(
                performance, "_old_goals_scored", performance.goals_scored
            ),
            "assists": getattr(performance, "_old_assists", performance.assists),
            "clean_sheets": getattr(
                performance, "_old_clean_sheets", performance.clean_sheets
            ),
            "saves": getattr(performance, "_old_saves", performance.saves),
            "penalties_saved": getattr(
                performance, "_old_penalties_saved", performance.penalties_saved
            ),
            "penalties_missed": getattr(
                performance, "_old_penalties_missed", performance.penalties_missed
            ),
            "own_goals": getattr(performance, "_old_own_goals", performance.own_goals),
            "yellow_cards": getattr(
                performance, "_old_yellow_cards", performance.yellow_cards
            ),
            "red_cards": getattr(performance, "_old_red_cards", performance.red_cards),
        }

        # Goals
        goals_diff = performance.goals_scored - old_values["goals_scored"]
        if goals_diff > 0:
            if position == "GKP":
                points += goals_diff * 6
            elif position == "DEF":
                points += goals_diff * 6
            elif position == "MID":
                points += goals_diff * 5
            else:  # FWD
                points += goals_diff * 4

        # Assists
        assists_diff = performance.assists - old_values["assists"]
        if assists_diff > 0:
            points += assists_diff * 3

        # Clean sheets
        clean_sheets_diff = performance.clean_sheets - old_values["clean_sheets"]
        if clean_sheets_diff > 0:
            if position in ["GKP", "DEF"]:
                points += clean_sheets_diff * 4
            elif position == "MID":
                points += clean_sheets_diff * 1

        # Saves (goalkeepers)
        saves_diff = performance.saves - old_values["saves"]
        if saves_diff > 0 and position == "GKP":
            points += saves_diff // 3

        # Penalties saved
        penalties_saved_diff = (
            performance.penalties_saved - old_values["penalties_saved"]
        )
        if penalties_saved_diff > 0:
            points += penalties_saved_diff * 5

        # Penalties missed
        penalties_missed_diff = (
            performance.penalties_missed - old_values["penalties_missed"]
        )
        if penalties_missed_diff > 0:
            points -= penalties_missed_diff * 2

        # Own goals
        own_goals_diff = performance.own_goals - old_values["own_goals"]
        if own_goals_diff > 0:
            points -= own_goals_diff * 2

        # Cards
        yellow_cards_diff = performance.yellow_cards - old_values["yellow_cards"]
        if yellow_cards_diff > 0:
            points -= yellow_cards_diff * 1

        red_cards_diff = performance.red_cards - old_values["red_cards"]
        if red_cards_diff > 0:
            points -= red_cards_diff * 3

        return points

    @staticmethod
    def _calculate_full(performance, position):
        """Calculate full points from scratch"""
        points = 0

        # Minutes played
        if performance.minutes_played > 0:
            points += 1
        if performance.minutes_played >= 60:
            points += 1

        # Goals
        if position == "GKP":
            points += performance.goals_scored * 6
        elif position == "DEF":
            points += performance.goals_scored * 6
        elif position == "MID":
            points += performance.goals_scored * 5
        else:  # FWD
            points += performance.goals_scored * 4

        # Assists
        points += performance.assists * 3

        # Clean sheets
        if position in ["GKP", "DEF"]:
            points += performance.clean_sheets * 4
        elif position == "MID":
            points += performance.clean_sheets * 1

        # Saves (goalkeepers)
        if position == "GKP":
            points += performance.saves // 3

        # Penalties
        points += performance.penalties_saved * 5
        points -= performance.penalties_missed * 2

        # Own goals
        points -= performance.own_goals * 2

        # Cards
        points -= performance.yellow_cards * 1
        points -= performance.red_cards * 3

        return points
