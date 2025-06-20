from apps.accounts.models import User
from rest_framework import serializers
from rest_framework import status
from apps.kpl.models import Player, Gameweek
from apps.kpl.serializers import PlayerSerializer, TeamSerializer
from apps.fantasy.models import (
    FantasyTeam, FantasyPlayer
)
from apps.kpl.models import Player

class FantasyTeamSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = FantasyTeam
        exclude = ("pkid", "created_at", "updated_at")
        read_only_fields = ('user', 'total_points', 'overall_rank', 'budget', 'gameweek', 'free_transfers', 'transfer_budget')

class FantasyPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyPlayer
        fields = ('id', 'name', 'position', 'team', 'price')
