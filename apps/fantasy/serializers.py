from rest_framework import serializers

from apps.fantasy.models import (
    FantasyPlayer,
    FantasyTeam,
    PlayerPerformance,
    TeamSelection,
)
from apps.kpl.models import Gameweek
from django.db.models import Sum
from decimal import Decimal


class FantasyTeamSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    gameweek = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField(read_only=True)
    total_points = serializers.SerializerMethodField(read_only=True)
    gameweek_points = serializers.SerializerMethodField(read_only=True)
    best_week = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FantasyTeam
        exclude = ("pkid", "created_at", "updated_at")
        read_only_fields = (
            "user",
            "total_points",
            "overall_rank",
            "budget",
            "gameweek",
            "free_transfers",
            "transfer_budget",
            "balance",
            "gameweek_points",
            "best_week",
        )

    def get_gameweek(self, obj):
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        return active_gameweek.number if active_gameweek else None

    def get_balance(self, obj):
        if not hasattr(obj, "players"):
            return 0.0

        total_players_value = obj.players.aggregate(total_value=Sum("current_value"))[
            "total_value"
        ] or Decimal("0.00")

        return float(Decimal(str(obj.budget)) - total_players_value)

    def get_gameweek_points(self, obj):
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        if not active_gameweek:
            return 0

        team_selection = TeamSelection.objects.filter(
            fantasy_team=obj, gameweek=active_gameweek
        ).first()

        if not team_selection:
            return 0

        starter_ids = team_selection.starters.values_list("player_id", flat=True)

        total_points = (
            PlayerPerformance.objects.filter(
                player_id__in=starter_ids, gameweek=active_gameweek
            ).aggregate(total=Sum("fantasy_points"))["total"]
            or 0
        )

        return total_points

    def get_total_points(self, obj):
        total = 0

        team_selections = TeamSelection.objects.filter(fantasy_team=obj).select_related(
            "gameweek", "captain", "vice_captain"
        )

        for selection in team_selections:
            starter_ids = selection.starters.values_list("player_id", flat=True)

            gameweek_points = (
                PlayerPerformance.objects.filter(
                    player_id__in=starter_ids, gameweek=selection.gameweek
                ).aggregate(total=Sum("fantasy_points"))["total"]
                or 0
            )

            total += gameweek_points

        return total

    def get_best_week(self, obj):
        team_selections = TeamSelection.objects.filter(fantasy_team=obj).select_related(
            "gameweek"
        )

        best_gameweek = None
        max_points = 0

        for selection in team_selections:
            starter_ids = selection.starters.values_list("player_id", flat=True)

            gameweek_points = (
                PlayerPerformance.objects.filter(
                    player_id__in=starter_ids, gameweek=selection.gameweek
                ).aggregate(total=Sum("fantasy_points"))["total"]
                or 0
            )

            if gameweek_points > max_points:
                max_points = gameweek_points
                best_gameweek = selection.gameweek.number

        return max_points if best_gameweek else None


class FantasyPlayerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="player.name", read_only=True)
    position = serializers.CharField(source="player.position", read_only=True)
    team = serializers.CharField(source="player.team.name", read_only=True)
    price = serializers.DecimalField(
        source="purchase_price", max_digits=6, decimal_places=2
    )
    jersey_image = serializers.SerializerMethodField(read_only=True)
    player = serializers.UUIDField(source="player.id", read_only=True)
    fantasy_team = serializers.UUIDField(source="fantasy_team.id", read_only=True)

    total_points = serializers.SerializerMethodField(read_only=True)
    current_value = serializers.SerializerMethodField(read_only=True)
    gameweek_points = serializers.SerializerMethodField(read_only=True)
    total_points_for_team = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FantasyPlayer
        fields = (
            "id",
            "name",
            "position",
            "team",
            "price",
            "fantasy_team",
            "player",
            "total_points",
            "is_captain",
            "is_vice_captain",
            "is_starter",
            "purchase_price",
            "current_value",
            "jersey_image",
            "gameweek_points",
            "total_points_for_team",
        )
        read_only_fields = (
            "total_points",
            "current_value",
            "jersey_image",
            "name",
            "position",
            "team",
            "player",
            "fantasy_team",
            "gameweek_points",
            "total_points_for_team",
        )

    def get_total_points(self, obj):
        total = obj.player.performances.aggregate(total_points=Sum("fantasy_points"))[
            "total_points"
        ]
        return total or 0

    def get_total_points_for_team(self, obj):
        team_selections = TeamSelection.objects.filter(
            fantasy_team=obj.fantasy_team, starters=obj, is_finalized=True
        ).values_list("gameweek_id", flat=True)

        total = (
            PlayerPerformance.objects.filter(
                player=obj.player, gameweek_id__in=team_selections
            ).aggregate(total=Sum("fantasy_points"))["total"]
            or 0
        )

        captain_selections = TeamSelection.objects.filter(
            fantasy_team=obj.fantasy_team, captain=obj, is_finalized=True
        ).values_list("gameweek_id", flat=True)

        captain_bonus = (
            PlayerPerformance.objects.filter(
                player=obj.player, gameweek_id__in=captain_selections
            ).aggregate(total=Sum("fantasy_points"))["total"]
            or 0
        )

        return total + captain_bonus

    def get_current_value(self, obj):
        return obj.player.current_value

    def get_gameweek_points(self, obj):
        try:
            active_gameweek = Gameweek.objects.filter(is_active=True).first()
            if not active_gameweek:
                return None

            team_selection = TeamSelection.objects.filter(
                fantasy_team=obj.fantasy_team, gameweek=active_gameweek, starters=obj
            ).first()

            if not team_selection:
                return None

            performance = obj.player.performances.filter(
                gameweek=active_gameweek
            ).first()

            if not performance:
                return None

            points = performance.fantasy_points

            return points

        except Exception:
            return None

    def get_jersey_image(self, obj):
        team = getattr(obj.player, "team", None)
        if team and team.jersey_image:
            return team.jersey_image.url
        return None

    def validate(self, data):
        fantasy_team = data.get("fantasy_team")
        player = data.get("player")
        instance = self.instance

        # Check max players in fantasy team
        if fantasy_team and fantasy_team.players.count() >= 15 and not instance:
            raise serializers.ValidationError(
                "You can't have more than 15 players in a fantasy team."
            )

        # Check max players from the same real team
        if player and fantasy_team:
            same_team_players = fantasy_team.players.filter(
                player__team=player.team
            ).exclude(pk=instance.pk if instance else None)
            if same_team_players.count() >= 3:
                raise serializers.ValidationError(
                    "You can't select more than 3 players from a single real team."
                )

        return data


class PlayerPerformanceSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source="player.name", read_only=True)
    team_name = serializers.CharField(source="player.team.name", read_only=True)

    class Meta:
        model = PlayerPerformance
        fields = [
            "id",
            "player_name",
            "team_name",
            "goals_scored",
            "assists",
            "yellow_cards",
            "red_cards",
            "clean_sheets",
            "saves",
            "own_goals",
            "penalties_saved",
            "penalties_missed",
            "minutes_played",
            "fantasy_points",
            "created_at",
            "updated_at",
        ]


class TeamSelectionSerializer(serializers.ModelSerializer):
    fantasy_team_name = serializers.CharField(
        source="fantasy_team.name", read_only=True
    )
    gameweek_number = serializers.IntegerField(source="gameweek.number", read_only=True)
    total_points = serializers.SerializerMethodField(read_only=True)
    starters_detail = FantasyPlayerSerializer(
        source="starters", many=True, read_only=True
    )
    bench_detail = FantasyPlayerSerializer(source="bench", many=True, read_only=True)

    class Meta:
        model = TeamSelection
        fields = (
            "id",
            "fantasy_team",
            "fantasy_team_name",
            "gameweek",
            "gameweek_number",
            "formation",
            "captain",
            "vice_captain",
            "starters",
            "bench",
            "starters_detail",
            "bench_detail",
            "is_finalized",
            "total_points",
        )

    def get_total_points(self, obj):
        if not obj.is_finalized:
            return 0

        starter_ids = obj.starters.values_list("player_id", flat=True)

        total_points = (
            PlayerPerformance.objects.filter(
                player_id__in=starter_ids, gameweek=obj.gameweek
            ).aggregate(total=Sum("fantasy_points"))["total"]
            or 0
        )

        return total_points
