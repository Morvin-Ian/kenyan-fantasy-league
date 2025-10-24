import logging
from typing import Dict, List

from django.db import transaction

from apps.kpl.models import Fixture, Team
from apps.fantasy.models import PlayerPerformance, FantasyPlayer, TeamSelection

logger = logging.getLogger(__name__)


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
    def _update_fantasy_team_points(player, fixture):
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

                    if is_starter:
                        performance = PlayerPerformance.objects.get(
                            player=player, fixture=fixture, gameweek=fixture.gameweek
                        )

                        points_to_add = performance.fantasy_points

                        fantasy_player.total_points += points_to_add
                        fantasy_player.save()

                        fantasy_team = fantasy_player.fantasy_team
                        fantasy_team.total_points += points_to_add
                        fantasy_team.save()

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
    def update_assists(fixture: Fixture, assists_data: List[Dict]) -> Dict:
        from apps.kpl.tasks.fixtures import find_player

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
                    performance.assists += count
                    is_captain = MatchEventService._get_captain_status(player, fixture)

                    if created:
                        performance.fantasy_points = (
                            FantasyPointsCalculator.calculate_full(
                                performance, is_captain
                            )
                        )
                    else:
                        incremental_points = (
                            FantasyPointsCalculator.calculate_incremental(
                                performance, old_values, is_captain
                            )
                        )
                        performance.fantasy_points += incremental_points

                    performance.save()
                    MatchEventService._update_fantasy_team_points(player, fixture)

                    updated_players.append(
                        {
                            "player_name": player.name,
                            "team": team.name,
                            "old_assists": old_values["assists"],
                            "new_assists": performance.assists,
                            "old_points": old_values["fantasy_points"],
                            "new_points": performance.fantasy_points,
                            "is_captain": is_captain,
                            "points_multiplier": 2 if is_captain else 1,
                            "created": created,
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
    def update_goals(fixture: Fixture, goals_data: List[Dict]) -> Dict:
        from apps.kpl.tasks.fixtures import find_player

        updated_players = []
        errors = []

        with transaction.atomic():
            for goal_data in goals_data:
                player_name = goal_data.get("player_name", "").strip()
                team_id = goal_data.get("team_id")
                count = goal_data.get("count", 1)

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

                    performance.goals_scored += count

                    is_captain = MatchEventService._get_captain_status(player, fixture)

                    if created:
                        performance.fantasy_points = (
                            FantasyPointsCalculator.calculate_full(
                                performance, is_captain
                            )
                        )
                    else:
                        incremental_points = (
                            FantasyPointsCalculator.calculate_incremental(
                                performance, old_values, is_captain
                            )
                        )
                        performance.fantasy_points += incremental_points

                    performance.save()
                    MatchEventService._update_fantasy_team_points(player, fixture)

                    updated_players.append(
                        {
                            "player_name": player.name,
                            "team": team.name,
                            "old_goals": old_values["goals_scored"],
                            "new_goals": performance.goals_scored,
                            "old_points": old_values["fantasy_points"],
                            "new_points": performance.fantasy_points,
                            "is_captain": is_captain,
                            "points_multiplier": 2 if is_captain else 1,
                            "created": created,
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
                    errors.append(
                        {"error": "player_out, player_in, and team_id are required"}
                    )
                    continue

                try:
                    team = Team.objects.get(id=team_id)

                    player_out = find_player(player_out_name)
                    if player_out:
                        is_captain_out = MatchEventService._get_captain_status(
                            player_out, fixture
                        )

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
                        perf_out.minutes_played = minute

                        if created_out:
                            perf_out.fantasy_points = (
                                FantasyPointsCalculator.calculate_full(
                                    perf_out, is_captain_out
                                )
                            )
                        else:
                            incremental_points = (
                                FantasyPointsCalculator.calculate_incremental(
                                    perf_out, old_values_out, is_captain_out
                                )
                            )
                            perf_out.fantasy_points += incremental_points

                        perf_out.save()
                        MatchEventService._update_fantasy_team_points(
                            player_out, fixture
                        )

                        updated_players.append(
                            {
                                "player_name": player_out.name,
                                "team": team.name,
                                "status": "substituted_out",
                                "old_minutes": old_values_out["minutes_played"],
                                "new_minutes": perf_out.minutes_played,
                                "old_points": old_values_out["fantasy_points"],
                                "new_points": perf_out.fantasy_points,
                                "is_captain": is_captain_out,
                                "points_multiplier": 2 if is_captain_out else 1,
                                "created": created_out,
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
                        is_captain_in = MatchEventService._get_captain_status(
                            player_in, fixture
                        )
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
                        perf_in.minutes_played = minutes_in

                        if created_in:
                            perf_in.fantasy_points = (
                                FantasyPointsCalculator.calculate_full(
                                    perf_in, is_captain_in
                                )
                            )
                        else:
                            incremental_points = (
                                FantasyPointsCalculator.calculate_incremental(
                                    perf_in, old_values_in, is_captain_in
                                )
                            )
                            perf_in.fantasy_points += incremental_points

                        perf_in.save()
                        MatchEventService._update_fantasy_team_points(
                            player_in, fixture
                        )

                        updated_players.append(
                            {
                                "player_name": player_in.name,
                                "team": team.name,
                                "status": "substituted_in",
                                "old_minutes": old_values_in["minutes_played"],
                                "new_minutes": perf_in.minutes_played,
                                "old_points": old_values_in["fantasy_points"],
                                "new_points": perf_in.fantasy_points,
                                "is_captain": is_captain_in,
                                "points_multiplier": 2 if is_captain_in else 1,
                                "created": created_in,
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
        from apps.kpl.tasks.fixtures import find_player

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
                    performance.minutes_played = minutes_played

                    is_captain = MatchEventService._get_captain_status(player, fixture)

                    if created:
                        performance.fantasy_points = (
                            FantasyPointsCalculator.calculate_full(
                                performance, is_captain
                            )
                        )
                    else:
                        incremental_points = (
                            FantasyPointsCalculator.calculate_incremental(
                                performance, old_values, is_captain
                            )
                        )
                        performance.fantasy_points += incremental_points

                    performance.save()
                    MatchEventService._update_fantasy_team_points(player, fixture)

                    updated_players.append(
                        {
                            "player_name": player.name,
                            "team": team.name,
                            "old_minutes": old_values["minutes_played"],
                            "new_minutes": performance.minutes_played,
                            "old_points": old_values["fantasy_points"],
                            "new_points": performance.fantasy_points,
                            "is_captain": is_captain,
                            "points_multiplier": 2 if is_captain else 1,
                            "created": created,
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
                    performance.clean_sheets += count

                    is_captain = MatchEventService._get_captain_status(player, fixture)

                    if created:
                        performance.fantasy_points = (
                            FantasyPointsCalculator.calculate_full(
                                performance, is_captain
                            )
                        )
                    else:
                        incremental_points = (
                            FantasyPointsCalculator.calculate_incremental(
                                performance, old_values, is_captain
                            )
                        )
                        performance.fantasy_points += incremental_points

                    performance.save()
                    MatchEventService._update_fantasy_team_points(player, fixture)

                    updated_players.append(
                        {
                            "player_name": player.name,
                            "team": team.name,
                            "old_clean_sheets": old_values["clean_sheets"],
                            "new_clean_sheets": performance.clean_sheets,
                            "old_points": old_values["fantasy_points"],
                            "new_points": performance.fantasy_points,
                            "is_captain": is_captain,
                            "points_multiplier": 2 if is_captain else 1,
                            "created": created,
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
    def _process_card(fixture, card_data, field_name, card_type):
        from apps.kpl.tasks.fixtures import find_player

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
            MatchEventService._update_fantasy_team_points(player, fixture)

            return {
                "success": True,
                "data": {
                    "player_name": player.name,
                    "team": team.name,
                    "card_type": card_type,
                    f"old_{field_name}": old_values[field_name],
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
    def _process_stat(fixture, stat_data, field_name):
        from apps.kpl.tasks.fixtures import find_player

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
            MatchEventService._update_fantasy_team_points(player, fixture)

            return {
                "success": True,
                "data": {
                    "player_name": player.name,
                    "team": team.name,
                    "stat_type": field_name,
                    f"old_{field_name}": old_values[field_name],
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
    def update_own_goals(fixture: Fixture, own_goals_data: List[Dict]) -> Dict:
        updated_players = []
        errors = []

        with transaction.atomic():
            for own_goal_data in own_goals_data:
                player_name = own_goal_data.get("player_name", "").strip()
                team_id = own_goal_data.get("team_id")
                count = own_goal_data.get("count", 1)

                if not player_name or not team_id:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error_code": "MISSING_REQUIRED_FIELDS",
                            "message": "player_name and team_id are required",
                        }
                    )
                    continue

                if count < 0:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error_code": "INVALID_COUNT",
                            "message": "count cannot be negative",
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
                                "error_code": "PLAYER_NOT_FOUND",
                                "message": f"Player not found in team {team.name}",
                            }
                        )
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
                    performance.own_goals += count

                    is_captain = MatchEventService._get_captain_status(player, fixture)

                    if created:
                        performance.fantasy_points = (
                            FantasyPointsCalculator.calculate_full(
                                performance, is_captain
                            )
                        )
                    else:
                        incremental_points = (
                            FantasyPointsCalculator.calculate_incremental(
                                performance, old_values, is_captain
                            )
                        )
                        performance.fantasy_points += incremental_points

                    performance.save()
                    MatchEventService._update_fantasy_team_points(player, fixture)

                    updated_players.append(
                        {
                            "player_name": player.name,
                            "team": team.name,
                            "old_own_goals": old_values["own_goals"],
                            "new_own_goals": performance.own_goals,
                            "old_points": old_values["fantasy_points"],
                            "new_points": performance.fantasy_points,
                            "points_deducted": (
                                abs(incremental_points)
                                if not created
                                else abs(
                                    performance.fantasy_points
                                    - old_values["fantasy_points"]
                                )
                            ),
                            "is_captain": is_captain,
                            "points_multiplier": 2 if is_captain else 1,
                            "created": created,
                        }
                    )

                except Team.DoesNotExist:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error_code": "TEAM_NOT_FOUND",
                            "message": f"Team with id {team_id} not found",
                        }
                    )
                except Exception as e:
                    logger.error(f"Error updating own goals for {player_name}: {e}")
                    errors.append(
                        {
                            "player_name": player_name,
                            "error_code": "UNEXPECTED_ERROR",
                            "message": str(e),
                        }
                    )

        return {
            "updated": len(updated_players),
            "failed": len(errors),
            "players": updated_players,
            "errors": errors,
        }
