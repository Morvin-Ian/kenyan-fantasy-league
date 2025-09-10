from rest_framework import serializers

from apps.kpl.models import Fixture, Player, Standing, Team


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
    is_active = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Fixture
        exclude = ("pkid", "created_at", "updated_at")
        
    def get_is_active(self, obj):
        if obj.gameweek:
            if obj.gameweek.is_active:
                return True
        return False


class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Player
        exclude = ("pkid", "created_at", "updated_at")
