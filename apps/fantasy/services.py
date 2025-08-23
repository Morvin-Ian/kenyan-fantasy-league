from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models import User
from apps.kpl.models import Player

from .models import FantasyPlayer, FantasyTeam, PlayerTransfer, Gameweek


class FantasyService:
    @staticmethod
    def create_fantasy_team(user: User, data: dict) -> FantasyTeam:
        return FantasyTeam.objects.create(user=user, **data)

    @staticmethod
    def update_fantasy_team(team: FantasyTeam, data: dict) -> FantasyTeam:
        for key, value in data.items():
            setattr(team, key, value)
        team.save()
        return team

    @staticmethod
    def delete_fantasy_team(team: FantasyTeam) -> None:
        team.delete()

    @staticmethod
    @transaction.atomic
    def save_team_players(
        formation:str, fantasy_team: FantasyTeam, starting_eleven: dict, bench_players: list
    ) -> dict:
        # Validate formation and team composition
        FantasyService._validate_team_composition(
            formation, fantasy_team, starting_eleven, bench_players
        )

        fantasy_team.formation = formation
        fantasy_team.save()
        
        all_player_ids = []
        players_to_update = {}

        goalkeeper = starting_eleven.get("goalkeeper")
        if goalkeeper:
            player_id = goalkeeper.get("player") or goalkeeper.get("id")
            all_player_ids.append(player_id)
            players_to_update[player_id] = FantasyService._build_player_data(
                goalkeeper, is_starter=True
            )

        for position in ["defenders", "midfielders", "forwards"]:
            position_players = starting_eleven.get(position, [])
            for player_data in position_players:
                player_id = player_data.get("player") or player_data.get("id")
                all_player_ids.append(player_id)
                players_to_update[player_id] = FantasyService._build_player_data(
                    player_data, is_starter=True
                )

        for player_data in bench_players:
            player_id = player_data.get("player") or player_data.get("id")
            all_player_ids.append(player_id)
            players_to_update[player_id] = FantasyService._build_player_data(
                player_data, is_starter=False
            )

        # Identify players to remove (transfers out)
        current_player_ids = set(str(fp.player.id) for fp in fantasy_team.players.all())
        new_player_ids = set(str(pid) for pid in all_player_ids)
        players_to_remove = current_player_ids - new_player_ids
        players_to_add = new_player_ids - current_player_ids

        # Calculate number of transfers
        num_transfers = len(players_to_remove)

        # Check transfer limits
        free_transfers = fantasy_team.free_transfers
        additional_transfers = max(0, num_transfers - free_transfers)
        transfer_cost = additional_transfers * 4  # 4 points per additional transfer

        if transfer_cost > float(fantasy_team.transfer_budget):
            raise ValidationError(
                f"Insufficient transfer budget. Required: {transfer_cost}, Available: {fantasy_team.transfer_budget}"
            )

        current_gameweek = Gameweek.objects.filter(is_active=True).first()
        if not current_gameweek:
            try:
                current_gameweek = Gameweek.objects.get(number=1)
            except Gameweek.DoesNotExist:
                raise ValidationError("No Gameweek with number 1 exists.")

        for player_id_out in players_to_remove:
            player_out = Player.objects.get(id=player_id_out)
            # For simplicity, assume one-to-one replacement or no direct replacement
            player_in_id = players_to_add.pop() if players_to_add else None
            player_in = Player.objects.get(id=player_in_id) if player_in_id else None
            transfer_cost_per_player = 4 if num_transfers > free_transfers else 0
            PlayerTransfer.objects.create(
                fantasy_team=fantasy_team,
                player_out=player_out,
                player_in=player_in,
                gameweek=current_gameweek,
                transfer_cost=transfer_cost_per_player,
            )

        if num_transfers > free_transfers:
            fantasy_team.transfer_budget -= transfer_cost
            fantasy_team.free_transfers = 0
        else:
            fantasy_team.free_transfers -= num_transfers
        fantasy_team.save()

        fantasy_team.players.exclude(player__id__in=all_player_ids).delete()

        existing_players = {
            str(fp.player.id): fp
            for fp in fantasy_team.players.filter(player__id__in=all_player_ids)
        }

        players_to_create = []
        players_to_bulk_update = []

        for player_id, update_data in players_to_update.items():
            player_id_str = str(player_id)
            if player_id_str in existing_players:
                # Update existing player
                fantasy_player = existing_players[player_id_str]
                for field, value in update_data.items():
                    setattr(fantasy_player, field, value)
                players_to_bulk_update.append(fantasy_player)
            else:
                # Create new player
                try:
                    player_instance = Player.objects.get(id=player_id)
                    fantasy_player = FantasyPlayer(
                        fantasy_team=fantasy_team,
                        player=player_instance,
                        total_points=0,
                        gameweek_added=current_gameweek,
                        **update_data,
                    )
                    players_to_create.append(fantasy_player)
                except Player.DoesNotExist:
                    continue

        if players_to_create:
            FantasyPlayer.objects.bulk_create(players_to_create)

        if players_to_bulk_update:
            FantasyPlayer.objects.bulk_update(
                players_to_bulk_update,
                [
                    "is_starter",
                    "is_captain",
                    "is_vice_captain",
                    "purchase_price",
                    "current_value",
                ],
            )

        fantasy_team.clean()

        return {
            "players_created": len(players_to_create),
            "players_updated": len(players_to_bulk_update),
            "transfers_made": num_transfers,
            "transfer_cost": transfer_cost,
            "remaining_free_transfers": fantasy_team.free_transfers,
            "remaining_transfer_budget": float(fantasy_team.transfer_budget),
        }

    @staticmethod
    def _build_player_data(player_data: dict, is_starter: bool) -> dict:
        return {
            "is_starter": is_starter,
            "is_captain": player_data.get("is_captain", False) if is_starter else False,
            "is_vice_captain": (
                player_data.get("is_vice_captain", False) if is_starter else False
            ),
            "purchase_price": player_data.get(
                "purchase_price", player_data.get("price", 0)
            ),
            "current_value": player_data.get(
                "current_value", player_data.get("price", 0)
            ),
        }

    @staticmethod
    def _validate_team_composition(
        formation:str, fantasy_team: FantasyTeam, starting_eleven: dict, bench_players: list
    ) -> None:
        formation_map = {
            "3-4-3": {"DEF": 3, "MID": 4, "FWD": 3, "GKP": 1},
            "3-5-2": {"DEF": 3, "MID": 5, "FWD": 2, "GKP": 1},
            "4-4-2": {"DEF": 4, "MID": 4, "FWD": 2, "GKP": 1},
            "4-3-3": {"DEF": 4, "MID": 3, "FWD": 3, "GKP": 1},
            "5-3-2": {"DEF": 5, "MID": 3, "FWD": 2, "GKP": 1},
            "5-4-1": {"DEF": 5, "MID": 4, "FWD": 1, "GKP": 1},
            "5-2-3": {"DEF": 5, "MID": 2, "FWD": 3, "GKP": 1},
        }
        bench_compositions = {
            "3-4-3": {"DEF": 2, "MID": 1, "FWD": 0, "GKP": 1},
            "3-5-2": {"DEF": 2, "MID": 0, "FWD": 1, "GKP": 1},
            "4-4-2": {"DEF": 1, "MID": 1, "FWD": 1, "GKP": 1},
            "4-3-3": {"DEF": 1, "MID": 2, "FWD": 0, "GKP": 1},
            "5-3-2": {"DEF": 0, "MID": 2, "FWD": 1, "GKP": 1},
            "5-4-1": {"DEF": 0, "MID": 1, "FWD": 2, "GKP": 1},
            "5-2-3": {"DEF": 0, "MID": 3, "FWD": 0, "GKP": 1},
        }

        # Count starters
        starter_counts = {"GKP": 0, "DEF": 0, "MID": 0, "FWD": 0}
        bench_counts = {"GKP": 0, "DEF": 0, "MID": 0, "FWD": 0}

        if starting_eleven.get("goalkeeper"):
            starter_counts["GKP"] += 1
        for position in ["defenders", "midfielders", "forwards"]:
            pos_key = {"defenders": "DEF", "midfielders": "MID", "forwards": "FWD"}[
                position
            ]
            starter_counts[pos_key] += len(starting_eleven.get(position, []))

        for player_data in bench_players:
            try:
                player = Player.objects.get(
                    id=player_data.get("player") or player_data.get("id")
                )
                bench_counts[player.position] += 1
            except Player.DoesNotExist:
                continue

        # Validate starter formation
        required_starters = formation_map[formation]
        for pos, required_count in required_starters.items():
            if starter_counts[pos] != required_count:
                raise ValidationError(
                    f"Formation {formation} requires {required_count} {pos} starters, you have {starter_counts[pos]}"
                )

        # Validate bench composition
        required_bench = bench_compositions[formation]
        for pos, required_count in required_bench.items():
            if bench_counts[pos] != required_count:
                raise ValidationError(
                    f"Formation {formation} requires {required_count} {pos} bench players, you have {bench_counts[pos]}"
                )

        # Validate total squad size
        total_players = sum(starter_counts.values()) + sum(bench_counts.values())
        if total_players != 15:
            raise ValidationError(
                f"Squad must have exactly 15 players, you have {total_players}"
            )

        # Validate budget
        total_value = 0
        for player_id in [
            starting_eleven.get("goalkeeper", {}).get("player")
            or starting_eleven.get("goalkeeper", {}).get("id")
        ]:
            if player_id:
                try:
                    total_value += float(Player.objects.get(id=player_id).current_value)
                except Player.DoesNotExist:
                    continue
        for position in ["defenders", "midfielders", "forwards"]:
            for player_data in starting_eleven.get(position, []):
                try:
                    total_value += float(
                        Player.objects.get(
                            id=player_data.get("player") or player_data.get("id")
                        ).current_value
                    )
                except Player.DoesNotExist:
                    continue
        for player_data in bench_players:
            try:
                total_value += float(
                    Player.objects.get(
                        id=player_data.get("player") or player_data.get("id")
                    ).current_value
                )
            except Player.DoesNotExist:
                continue

        if total_value > float(fantasy_team.budget):
            raise ValidationError(
                f"Team value {total_value} exceeds budget {fantasy_team.budget}"
            )
