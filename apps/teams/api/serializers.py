
from rest_framework import serializers
from teams.models import Team, Player, Coach, Gameweek, Match, PlayerStatistics

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    team_name = serializers.ReadOnlyField(source='team.name')
    full_name = serializers.ReadOnlyField(source='user.get_full_name')

    class Meta:
        model = Player
        fields = ['id', 'full_name', 'team', 'team_name', 'jersey_number', 'position', 'price']

class CoachSerializer(serializers.ModelSerializer):
    team_name = serializers.ReadOnlyField(source='team.name')
    full_name = serializers.ReadOnlyField(source='user.get_full_name')

    class Meta:
        model = Coach
        fields = ['id', 'full_name', 'team', 'team_name', 'role', 'start_date']

class GameweekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gameweek
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    home_team_name = serializers.ReadOnlyField(source='home_team.name')
    away_team_name = serializers.ReadOnlyField(source='away_team.name')

    class Meta:
        model = Match
        fields = ['id', 'home_team', 'home_team_name', 'away_team', 'away_team_name', 'gameweek', 'date', 'venue', 'home_score', 'away_score']

class PlayerStatisticsSerializer(serializers.ModelSerializer):
    player_name = serializers.ReadOnlyField(source='player.user.get_full_name')
    team_name = serializers.ReadOnlyField(source='player.team.name')

    class Meta:
        model = PlayerStatistics
        fields = '__all__'

class PlayerStatisticsDetailSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    gameweek = GameweekSerializer()

    class Meta:
        model = PlayerStatistics
        fields = '__all__'