from django.core.exceptions import ValidationError
from rest_framework import serializers, status

from apps.accounts.models import User
from apps.fantasy.models import FantasyPlayer, FantasyTeam
from apps.kpl.models import Gameweek, Player
from apps.kpl.serializers import PlayerSerializer, TeamSerializer


class FantasyTeamSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

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


class FantasyPlayerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="player.name", read_only=True)
    position = serializers.CharField(source="player.position", read_only=True)
    team = serializers.CharField(source="player.team.name", read_only=True)
    price = serializers.DecimalField(
        source="purchase_price", max_digits=6, decimal_places=2
    )
    jersey_image = serializers.ImageField(
        source="player.team.jersey_image", read_only=True
    )
    player = serializers.UUIDField(
        source="player.id", read_only=True
    )  # Return player.id
    fantasy_team = serializers.UUIDField(
        source="fantasy_team.id", read_only=True
    )  # Return fantasy_team.id

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
            "gameweek",
            "total_points",
            "gameweek_points",
            "is_captain",
            "is_vice_captain",
            "is_starter",
            "purchase_price",
            "current_value",
            "jersey_image",
        )
        read_only_fields = (
            "total_points",
            "gameweek_points",
            "current_value",
            "jersey_image",
            "name",
            "position",
            "team",
            "player",
            "fantasy_team",
        )

    # def validate(self, data):
    #     """
    #     Custom validation to enforce model constraints:
    #     - Max 15 players per fantasy team
    #     - Max 3 players from the same real team
    #     """
    #     fantasy_team = data.get('fantasy_team')
    #     player = data.get('player')
    #     instance = self.instance

    #     # Check max players in fantasy team
    #     if fantasy_team and fantasy_team.players.count() >= 15 and not instance:
    #         raise serializers.ValidationError(
    #             "You can't have more than 15 players in a fantasy team."
    #         )

    #     # Check max players from the same real team
    #     if player and fantasy_team:
    #         same_team_players = fantasy_team.players.filter(
    #             player__team=player.team
    #         ).exclude(pk=instance.pk if instance else None)
    #         if same_team_players.count() >= 3:
    #             raise serializers.ValidationError(
    #                 "You can't select more than 3 players from a single real team."
    #             )

    #     return data

    # def create(self, validated_data):
    #     """
    #     Create a new FantasyPlayer instance with validated data.
    #     """
    #     return FantasyPlayer.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     """
    #     Update an existing FantasyPlayer instance with validated data.
    #     """
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance
