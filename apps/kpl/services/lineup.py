import csv
import io
import logging
from typing import Dict, List, Tuple

from django.db import transaction
from django.core.cache import cache

from apps.kpl.models import (
    Fixture,
    FixtureLineup,
    FixtureLineupPlayer,
    Player,
    Team,
)
from apps.fantasy.models import PlayerPerformance
from apps.kpl.tasks.fixtures import find_player

logger = logging.getLogger(__name__)


class LineupService:
    """Service for handling fixture lineup operations"""

    @staticmethod
    def upload_lineup_from_csv(
        csv_file,
        fixture_id: str,
        team_id: str,
        side: str = None,
        auto_update_performance: bool = True,
    ) -> Dict:
        """
        Upload lineup from CSV file and optionally update player performances

        Returns:
            Dict with lineup data, counts, errors, and message
        """
        try:
            fixture = Fixture.objects.select_related(
                "home_team", "away_team", "gameweek"
            ).get(id=fixture_id)
        except Fixture.DoesNotExist:
            raise ValueError("Fixture not found")

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise ValueError("Team not found")

        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
        except Exception as e:
            raise ValueError(f"Could not read CSV: {str(e)}")

        players_to_add = []
        errors = []

        for i, row in enumerate(reader):
            name = row.get("name")
            position = row.get("position")
            is_bench = row.get("is_bench", "").lower() in ["true", "1", "yes"]
            minutes_played = int(row.get("minutes_played", 90 if not is_bench else 0))

            if not name or not position:
                errors.append({"index": i, "error": "Missing name or position"})
                continue

            player = Player.objects.filter(name__iexact=name, team=team).first()
            if not player:
                errors.append(
                    {"index": i, "name": name, "error": "Player not found in team"}
                )
                continue

            players_to_add.append(
                {
                    "player": player,
                    "position": position,
                    "order_index": i + 1,
                    "is_bench": is_bench,
                    "minutes_played": minutes_played,
                }
            )

        if not players_to_add:
            raise ValueError("No valid players found in CSV")

        performance_count = 0

        with transaction.atomic():
            lineup, created = FixtureLineup.objects.get_or_create(
                fixture=fixture,
                team=team,
                defaults={
                    "side": side
                    or (
                        "home"
                        if fixture.home_team == team
                        else "away" if fixture.away_team == team else None
                    ),
                    "is_confirmed": True,
                    "source": "csv_upload",
                },
            )

            if not lineup.side:
                raise ValueError(
                    "Could not determine lineup side. Please provide 'side'."
                )

            lineup.players.all().delete()

            lineup_players = [
                FixtureLineupPlayer(
                    lineup=lineup,
                    player=p["player"],
                    position=p["position"],
                    order_index=p["order_index"],
                    is_bench=p["is_bench"],
                )
                for p in players_to_add
            ]
            FixtureLineupPlayer.objects.bulk_create(lineup_players)

            if auto_update_performance:
                try:
                    from apps.fantasy.tasks.player_performance import (
                        update_complete_player_performance,
                    )

                    home_lineup_exists = fixture.lineups.filter(
                        team=fixture.home_team
                    ).exists()
                    away_lineup_exists = fixture.lineups.filter(
                        team=fixture.away_team
                    ).exists()

                    if home_lineup_exists and away_lineup_exists:
                        performance_count = update_complete_player_performance(fixture)

                except Exception as e:
                    logger.error(f"Error updating player performances: {str(e)}")
                    errors.append(
                        {
                            "type": "performance_update",
                            "error": f"Failed to update player performances: {str(e)}",
                        }
                    )

        return {
            "lineup": lineup,
            "created_count": len(players_to_add),
            "performance_updated": performance_count > 0,
            "performance_count": performance_count,
            "errors": errors,
        }
