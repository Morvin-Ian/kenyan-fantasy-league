import csv
import io
import logging
from typing import Dict

from django.db import transaction
from django.core.cache import cache

from apps.kpl.models import (
    Player,
    Team,
)
from apps.kpl.tasks.fixtures import find_player

logger = logging.getLogger(__name__)


class PlayerService:
    """Service for handling player operations"""

    @staticmethod
    def bulk_upload_from_csv(csv_file) -> Dict:
        """
        Bulk upload/update players from CSV file

        Returns:
            Dict with created_players, updated_players, and errors
        """
        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
        except Exception as e:
            raise ValueError(f"Could not read CSV file: {str(e)}")

        created_players = []
        updated_players = []
        errors = []

        with transaction.atomic():
            for i, row in enumerate(reader):
                try:
                    name = row.get("name")
                    team_name = row.get("team")
                    position = row.get("position")
                    jersey_number = row.get("jersey")
                    age = row.get("age")
                    current_value = row.get("value")

                    if not all([name, team_name, position]):
                        errors.append(
                            {
                                "index": i,
                                "error": "Missing one or more required fields.",
                            }
                        )
                        continue

                    try:
                        jersey_number = int(jersey_number) if jersey_number else None
                        age = int(age) if age else None
                        current_value = float(current_value) if current_value else 5.0
                    except ValueError:
                        errors.append(
                            {
                                "index": i,
                                "name": name,
                                "error": "Invalid data type for jersey_number, age, or current_value",
                            }
                        )
                        continue

                    team = Team.objects.filter(name=team_name).first()
                    if not team:
                        errors.append(
                            {
                                "index": i,
                                "name": name,
                                "error": f"Team '{team_name}' not found",
                            }
                        )
                        continue

                    existing_player = find_player(name)

                    if existing_player:
                        updated_fields = []
                        if existing_player.team != team:
                            existing_player.team = team
                            updated_fields.append("team")
                        if existing_player.position != position:
                            existing_player.position = position
                            updated_fields.append("position")
                        if existing_player.jersey_number != jersey_number:
                            existing_player.jersey_number = jersey_number
                            updated_fields.append("jersey_number")
                        if existing_player.age != age:
                            existing_player.age = age
                            updated_fields.append("age")
                        if existing_player.current_value != current_value:
                            existing_player.current_value = current_value
                            updated_fields.append("current_value")

                        if updated_fields:
                            existing_player.save(update_fields=updated_fields)
                            updated_players.append(
                                {"name": name, "updated_fields": updated_fields}
                            )
                    else:
                        player = Player.objects.create(
                            name=name,
                            team=team,
                            position=position,
                            jersey_number=jersey_number,
                            age=age,
                            current_value=current_value,
                        )
                        created_players.append(player)

                except Exception as e:
                    errors.append(
                        {
                            "index": i,
                            "name": row.get("name", "Unknown"),
                            "error": str(e),
                        }
                    )

        # Clear relevant cache
        cache.delete_many(cache.keys("players_active_list_*"))

        return {
            "created_players": created_players,
            "updated_players": updated_players,
            "errors": errors,
        }
