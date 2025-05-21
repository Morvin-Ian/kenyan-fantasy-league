from rest_framework import serializers
from apps.kpl.models import Player, Gameweek
from apps.kpl.api.serializers import PlayerSerializer, TeamSerializer
from apps.fantasy.models import (
    FantasyTeam
)


class FantasyTeamSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = FantasyTeam
        exclude = ("pkid", "created_at", "updated_at")
        read_only_fields = ('user', 'total_points', 'overall_rank', 'budget', 'gameweek', 'free_transfers', 'transfer_budget')

    def create(self, validated_data):
        user = self.context['request'].user
        return FantasyTeam.objects.create(user=user, **validated_data)