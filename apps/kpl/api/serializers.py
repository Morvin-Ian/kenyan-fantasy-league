from rest_framework import serializers
from apps.kpl.models import Team, Standing, Fixture, Player

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        exclude = ("pkid", "created_at", "updated_at")

class StandingSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)  

    class Meta:
        model = Standing
        exclude = ("pkid", "created_at", "updated_at")

class FixtureSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(read_only=True)  
    away_team = TeamSerializer(read_only=True) 

    class Meta:
        model = Fixture
        exclude = ("pkid", "created_at", "updated_at")
class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)  
    class Meta:
        model = Player
        exclude = ("pkid", "created_at", "updated_at")