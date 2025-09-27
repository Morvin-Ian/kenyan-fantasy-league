from rest_framework import serializers

from apps.fantasy.models import FantasyPlayer, FantasyTeam, PlayerPerformance
from apps.kpl.models import Gameweek


class FantasyTeamSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    gameweek = serializers.SerializerMethodField()

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
        )

    def get_gameweek(self, obj):
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        return active_gameweek.number if active_gameweek else None


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
        )

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

    def get_jersey_image(self, obj):
        team = getattr(obj.player, "team", None)
        if team and team.jersey_image:
            return team.jersey_image.url
        return None


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
