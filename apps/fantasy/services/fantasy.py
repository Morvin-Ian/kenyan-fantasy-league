import random
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.fantasy import scoring
from apps.kpl.models import Player

from ..models import (
    Chip,
    ChipType,
    FantasyPlayer,
    FantasyTeam,
    Gameweek,
    PlayerTransfer,
    TeamSelection,
)


class FantasyService:
    @staticmethod
    def create_fantasy_team(user: User, data: dict) -> FantasyTeam:
        team = FantasyTeam.objects.create(user=user, **data)

        chips_to_create = [
            Chip(fantasy_team=team, chip_type=chip_type, is_used=False)
            for chip_type in ChipType.values
        ]
        Chip.objects.bulk_create(chips_to_create)

        return team

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
        formation: str,
        fantasy_team: FantasyTeam,
        starting_eleven: dict,
        bench_players: list,
    ) -> dict:
        current_gameweek = Gameweek.objects.filter(is_active=True).first()
        if not current_gameweek:
            try:
                current_gameweek = Gameweek.objects.get(number=1)
            except Gameweek.DoesNotExist:
                raise ValidationError("No Gameweek with number 1 exists.")

        existing_selection = TeamSelection.objects.filter(
            fantasy_team=fantasy_team, gameweek=current_gameweek
        ).first()

        is_first_team = not TeamSelection.objects.filter(
            fantasy_team=fantasy_team
        ).exists()

        if current_gameweek.is_deadline_passed:
            if existing_selection:
                raise ValidationError(
                    f"Gameweek {current_gameweek.number} transfer deadline has passed. "
                    "You cannot make changes to your team."
                )
            else:
                next_gameweek = (
                    Gameweek.objects.filter(number__gt=current_gameweek.number)
                    .order_by("number")
                    .first()
                )

                if not next_gameweek:
                    next_gameweek = Gameweek.objects.create(
                        number=current_gameweek.number + 1,
                        start_date=timezone.now().date() + timezone.timedelta(days=7),
                        end_date=timezone.now().date() + timezone.timedelta(days=14),
                        transfer_deadline=timezone.now() + timezone.timedelta(days=6),
                        is_active=False,
                    )

                target_gameweek = next_gameweek
        else:
            target_gameweek = current_gameweek

        FantasyService._validate_team_composition(
            formation, fantasy_team, starting_eleven, bench_players
        )

        has_captain = False
        has_vice_captain = False

        goalkeeper = starting_eleven.get("goalkeeper")
        if goalkeeper:
            has_captain = has_captain or goalkeeper.get("is_captain", False)
            has_vice_captain = has_vice_captain or goalkeeper.get(
                "is_vice_captain", False
            )

        for position in ["defenders", "midfielders", "forwards"]:
            position_players = starting_eleven.get(position, [])
            for player_data in position_players:
                has_captain = has_captain or player_data.get("is_captain", False)
                has_vice_captain = has_vice_captain or player_data.get(
                    "is_vice_captain", False
                )

        # If no captain or vice-captain assigned, assign them randomly
        if not has_captain or not has_vice_captain:
            starting_eleven = FantasyService._assign_captain_and_vice(
                starting_eleven, has_captain, has_vice_captain
            )

        fantasy_team.formation = formation
        fantasy_team.save()

        all_player_ids = []
        players_to_update = {}
        captain_id = None
        vice_captain_id = None
        starter_ids = []

        # Every price written to the squad comes from here, so the request body
        # cannot set what a player was bought for.
        submitted_ids = [
            entry.get("player") or entry.get("id")
            for entry in (
                [starting_eleven.get("goalkeeper")]
                + [
                    player
                    for key in ("defenders", "midfielders", "forwards")
                    for player in starting_eleven.get(key, [])
                ]
                + list(bench_players)
            )
            if entry
        ]
        prices = {
            str(player.id): player.current_value
            for player in Player.objects.filter(id__in=submitted_ids)
        }

        goalkeeper = starting_eleven.get("goalkeeper")
        if goalkeeper:
            player_id = goalkeeper.get("player") or goalkeeper.get("id")
            all_player_ids.append(player_id)
            starter_ids.append(player_id)
            players_to_update[player_id] = FantasyService._build_player_data(
                goalkeeper, is_starter=True, price=prices.get(str(player_id))
            )
            if goalkeeper.get("is_captain"):
                captain_id = player_id
            if goalkeeper.get("is_vice_captain"):
                vice_captain_id = player_id

        for position in ["defenders", "midfielders", "forwards"]:
            position_players = starting_eleven.get(position, [])
            for player_data in position_players:
                player_id = player_data.get("player") or player_data.get("id")
                all_player_ids.append(player_id)
                starter_ids.append(player_id)
                players_to_update[player_id] = FantasyService._build_player_data(
                    player_data, is_starter=True, price=prices.get(str(player_id))
                )
                if player_data.get("is_captain"):
                    captain_id = player_id
                if player_data.get("is_vice_captain"):
                    vice_captain_id = player_id

        # The client sends the bench as an ordered list; that order is who comes
        # on first when a starter does not play.
        bench_order = {}
        for index, player_data in enumerate(bench_players, start=1):
            player_id = player_data.get("player") or player_data.get("id")
            all_player_ids.append(player_id)
            bench_order[str(player_id)] = index
            players_to_update[player_id] = FantasyService._build_player_data(
                player_data, is_starter=False, price=prices.get(str(player_id))
            )

        num_transfers = 0
        transfer_cost = 0

        if not is_first_team:
            current_player_ids = set(
                str(fp.player.id) for fp in fantasy_team.players.all()
            )
            new_player_ids = set(str(pid) for pid in all_player_ids)
            players_to_remove = current_player_ids - new_player_ids
            players_to_add = new_player_ids - current_player_ids

            num_transfers = len(players_to_remove)

            free_transfers = fantasy_team.free_transfers
            additional_transfers = max(0, num_transfers - free_transfers)
            # A transfer beyond the free allowance costs points, not money. This
            # used to be charged against transfer_budget, a DecimalField that
            # defaults to 0.00, so the check below rejected every extra transfer
            # outright and the -4 hit could never actually be taken.
            transfer_cost = additional_transfers * abs(scoring.TRANSFER_HIT_POINTS)

            # Handle transfers
            paid_transfers = additional_transfers
            for player_id_out in players_to_remove:
                player_out = Player.objects.get(id=player_id_out)
                player_in_id = players_to_add.pop() if players_to_add else None
                player_in = (
                    Player.objects.get(id=player_in_id) if player_in_id else None
                )
                # Only the transfers beyond the free allowance are charged. The
                # previous version tagged every transfer in the batch with 4, so
                # three transfers on one free transfer recorded a cost of 12
                # against a hit of 8.
                charged = paid_transfers > 0
                if charged:
                    paid_transfers -= 1
                transfer_cost_per_player = (
                    abs(scoring.TRANSFER_HIT_POINTS) if charged else 0
                )
                PlayerTransfer.objects.create(
                    fantasy_team=fantasy_team,
                    player_out=player_out,
                    player_in=player_in,
                    gameweek=current_gameweek,
                    transfer_cost=transfer_cost_per_player,
                )

            if num_transfers > free_transfers:
                fantasy_team.free_transfers = 0
            else:
                fantasy_team.free_transfers -= num_transfers
        else:
            # First team - just clear any existing players (shouldn't happen, but safety)
            fantasy_team.players.all().delete()

        # Remove players not in squad (if not first team)
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

        FantasyService._update_team_value(fantasy_team)
        team_selection = FantasyService._create_team_selection(
            fantasy_team=fantasy_team,
            gameweek=target_gameweek,
            formation=formation,
            captain_id=captain_id,
            vice_captain_id=vice_captain_id,
            starter_ids=starter_ids,
            bench_order=bench_order,
            transfer_hit=-transfer_cost,
        )

        return {
            "players_created": len(players_to_create),
            "players_updated": len(players_to_bulk_update),
            "transfers_made": num_transfers,
            "transfer_cost": transfer_cost,
            "points_hit": -transfer_cost,
            "remaining_free_transfers": fantasy_team.free_transfers,
            "remaining_transfer_budget": float(fantasy_team.transfer_budget),
            "team_selection_id": str(team_selection.id),
            "gameweek": current_gameweek.number,
            "is_first_team": is_first_team,
            "current_team_value": float(fantasy_team.budget),
        }

    @staticmethod
    def _update_team_value(fantasy_team: FantasyTeam) -> None:
        """Update the fantasy team's budget to reflect current player values"""
        # Refresh from database to ensure we get all newly created players
        fantasy_team.refresh_from_db()

        total_value = (
            fantasy_team.players.aggregate(total=models.Sum("current_value"))["total"]
            or 0
        )

        fantasy_team.budget = total_value
        fantasy_team.save(update_fields=["budget"])

    @staticmethod
    def _create_team_selection(  # noqa: PLR0913 - one call site, all required
        fantasy_team: FantasyTeam,
        gameweek: Gameweek,
        formation: str,
        captain_id: str,
        vice_captain_id: str,
        starter_ids: list,
        bench_order: dict = None,
        transfer_hit: int = 0,
    ) -> TeamSelection:
        """Create or update the team selection for a gameweek.

        ``transfer_hit`` is the points deduction for transfers beyond the free
        allowance, stored on the gameweek it applies to so the scoring engine
        can subtract it and the client can show gross and net separately.

        ``bench_order`` is ``{player id: position on the bench}``, which decides
        who comes on first when a starter does not play.
        """
        captain = FantasyPlayer.objects.get(
            fantasy_team=fantasy_team, player__id=captain_id
        )
        vice_captain = FantasyPlayer.objects.get(
            fantasy_team=fantasy_team, player__id=vice_captain_id
        )
        starters = FantasyPlayer.objects.filter(
            fantasy_team=fantasy_team, player__id__in=starter_ids
        )

        bench = FantasyPlayer.objects.filter(fantasy_team=fantasy_team).exclude(
            player__id__in=starter_ids
        )

        team_selection, created = TeamSelection.objects.get_or_create(
            fantasy_team=fantasy_team,
            gameweek=gameweek,
            defaults={
                "formation": formation,
                "captain": captain,
                "vice_captain": vice_captain,
                "is_finalized": False,
                "transfer_hit": transfer_hit,
            },
        )

        if not created:
            team_selection.formation = formation
            team_selection.captain = captain
            team_selection.vice_captain = vice_captain
            # Hits accumulate across several saves inside one gameweek.
            team_selection.transfer_hit += transfer_hit
            team_selection.save()

        team_selection.starters.set(starters)
        team_selection.bench.set(bench)

        if bench_order:
            for fantasy_player in bench:
                order = bench_order.get(str(fantasy_player.player_id))
                if order is not None and fantasy_player.bench_order != order:
                    fantasy_player.bench_order = order
                    fantasy_player.save(update_fields=["bench_order", "updated_at"])

        return team_selection

    @staticmethod
    def _assign_captain_and_vice(
        starting_eleven: dict, has_captain: bool, has_vice_captain: bool
    ) -> dict:
        """Assign captain and vice-captain randomly if not already assigned"""
        all_starters = []

        goalkeeper = starting_eleven.get("goalkeeper")
        if goalkeeper:
            all_starters.append(("goalkeeper", goalkeeper))

        for position in ["defenders", "midfielders", "forwards"]:
            position_players = starting_eleven.get(position, [])
            for player_data in position_players:
                all_starters.append((position, player_data))

        if not has_captain:
            pos_idx = random.randint(0, len(all_starters) - 1)
            position_key, captain_player = all_starters[pos_idx]

            if position_key == "goalkeeper":
                starting_eleven["goalkeeper"]["is_captain"] = True
            else:
                player_list = starting_eleven[position_key]
                for i, player in enumerate(player_list):
                    player_id = player.get("player") or player.get("id")
                    captain_id = captain_player.get("player") or captain_player.get(
                        "id"
                    )
                    if str(player_id) == str(captain_id):
                        starting_eleven[position_key][i]["is_captain"] = True
                        break

            all_starters.pop(pos_idx)

        if not has_vice_captain and all_starters:
            pos_idx = random.randint(0, len(all_starters) - 1)
            position_key, vice_captain_player = all_starters[pos_idx]

            if position_key == "goalkeeper":
                starting_eleven["goalkeeper"]["is_vice_captain"] = True
            else:
                player_list = starting_eleven[position_key]
                for i, player in enumerate(player_list):
                    player_id = player.get("player") or player.get("id")
                    vice_captain_id = vice_captain_player.get(
                        "player"
                    ) or vice_captain_player.get("id")
                    if str(player_id) == str(vice_captain_id):
                        starting_eleven[position_key][i]["is_vice_captain"] = True
                        break

        return starting_eleven

    @staticmethod
    def _build_player_data(
        player_data: dict, is_starter: bool, price: Optional[Decimal] = None
    ) -> dict:
        """Build the stored fields for one squad member.

        Prices are taken from the ``Player`` row rather than the request body.
        They used to be read straight off ``player_data``, so a caller could
        post any purchase price it liked — the budget check read the database
        but the value that was *stored* came from the client, which is what
        later sell-price and profit maths is based on.
        """
        return {
            "is_starter": is_starter,
            "is_captain": player_data.get("is_captain", False) if is_starter else False,
            "is_vice_captain": (
                player_data.get("is_vice_captain", False) if is_starter else False
            ),
            "purchase_price": price if price is not None else Decimal("0"),
            "current_value": price if price is not None else Decimal("0"),
        }

    @staticmethod
    def _validate_team_composition(
        formation: str,
        fantasy_team: FantasyTeam,
        starting_eleven: dict,
        bench_players: list,
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

        # Counted by the position the database holds, not by which array the
        # client put the player in. Only the bench used to be checked this way,
        # so an eleven of forwards submitted as "defenders" passed validation —
        # and then scored as forwards, because that is what the scoring engine
        # reads. The client also rewrites a player's position locally when you
        # swap across positions, which made that easy to trigger by accident.
        submitted_positions = {}
        goalkeeper = starting_eleven.get("goalkeeper")
        if goalkeeper:
            submitted_positions[goalkeeper.get("player") or goalkeeper.get("id")] = (
                "goalkeeper"
            )
        for position in ["defenders", "midfielders", "forwards"]:
            for player_data in starting_eleven.get(position, []):
                submitted_positions[
                    player_data.get("player") or player_data.get("id")
                ] = position

        expected_for_slot = {
            "goalkeeper": "GKP",
            "defenders": "DEF",
            "midfielders": "MID",
            "forwards": "FWD",
        }
        for player_id, slot in submitted_positions.items():
            try:
                player = Player.objects.get(id=player_id)
            except Player.DoesNotExist:
                continue
            starter_counts[player.position] += 1
            if player.position != expected_for_slot[slot]:
                raise ValidationError(
                    f"{player.name} is a {player.get_position_display()} and cannot "
                    f"be played in the {slot} line."
                )

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

        # Validate budget - only check initial budget (70.00), not current value
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

        has_existing_players = fantasy_team.players.exists()

        if not has_existing_players and total_value > 70.00:
            raise ValidationError(
                f"Team value {total_value} exceeds initial budget of 70.00"
            )
