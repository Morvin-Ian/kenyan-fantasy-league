from apps.accounts.models import User
from rest_framework import serializers
from rest_framework import status
from apps.kpl.models import Player, Gameweek
from apps.kpl.api.serializers import PlayerSerializer, TeamSerializer
from apps.fantasy.models import (
    FantasyTeam
)

from util.errors.exception_handler import CustomInternalServerError

class FantasyTeamSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = FantasyTeam
        exclude = ("pkid", "created_at", "updated_at")
        read_only_fields = ('user', 'total_points', 'overall_rank', 'budget', 'gameweek', 'free_transfers', 'transfer_budget')

    def create(self, validated_data):
        try:
            team = FantasyTeam.objects.filter(user__id=self.context['request'].user.id)
            user = User.objects.get(id=self.context['request'].user.id)
        
            if team.exists():    
                raise CustomInternalServerError(
                    message="You already have a fantasy team.",
                    status_code=status.HTTP_400_BAD_REQUEST  
                )
            team_name = validated_data.get('name')
            if FantasyTeam.objects.filter(name__iexact=team_name).exists():
                raise CustomInternalServerError(
                    message=f"A team with the name '{team_name}' already exists.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            return FantasyTeam.objects.create(user=user, **validated_data)
        except CustomInternalServerError as api_exec:
            raise api_exec
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=500
            )