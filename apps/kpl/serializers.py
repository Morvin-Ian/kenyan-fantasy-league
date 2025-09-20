from rest_framework import serializers

from apps.kpl.models import Fixture, FixtureLineup, FixtureLineupPlayer, Player, Standing, Team


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
    lineup_status = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Fixture
        exclude = ("pkid", "created_at", "updated_at")
        
    def get_is_active(self, obj):
        if obj.gameweek:
            if obj.gameweek.is_active:
                return True
        return False

    def get_lineup_status(self, obj: Fixture):
        request = self.context.get("request") if hasattr(self, "context") else None
        include = False
        if request:
            include = request.query_params.get("include") == "lineups=true"
        if not include:
            return None
        qs = getattr(obj, "lineups", None)
        if not qs:
            return {"available": False}
        has_home = qs.filter(side="home").exists()
        has_away = qs.filter(side="away").exists()
        confirmed_home = qs.filter(side="home", is_confirmed=True).exists()
        confirmed_away = qs.filter(side="away", is_confirmed=True).exists()
        status = "NA"
        if has_home or has_away:
            status = "Predicted"
        if confirmed_home and confirmed_away:
            status = "Confirmed"
        return {
            "available": has_home or has_away,
            "confirmed": confirmed_home and confirmed_away,
            "status": status,
        }


class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Player
        exclude = ("pkid", "created_at", "updated_at")


class FixtureLineupPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = FixtureLineupPlayer
        exclude = ("pkid", "created_at", "updated_at")


class FixtureLineupSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    players = FixtureLineupPlayerSerializer(many=True, read_only=True)

    class Meta:
        model = FixtureLineup
        exclude = ("pkid", "created_at", "updated_at")


class FixtureLineupDetailSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    starters = serializers.SerializerMethodField()
    bench = serializers.SerializerMethodField()

    class Meta:
        model = FixtureLineup
        fields = (
            "id",
            "team",
            "side",
            "formation",
            "is_confirmed",
            "source",
            "published_at",
            "starters",
            "bench",
        )

    def get_starters(self, obj: FixtureLineup):
        qs = obj.players.filter(is_bench=False).select_related("player")
        return FixtureLineupPlayerSerializer(qs, many=True).data

    def get_bench(self, obj: FixtureLineup):
        qs = obj.players.filter(is_bench=True).select_related("player")
        return FixtureLineupPlayerSerializer(qs, many=True).data


class ManualLineupPlayerInputSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    jersey_number = serializers.IntegerField(required=False, allow_null=True)
    role = serializers.CharField(required=False, allow_blank=True)
    position_guess = serializers.CharField(required=False, allow_blank=True)


class ManualLineupInputSerializer(serializers.Serializer):
    side = serializers.ChoiceField(choices=[("home", "home"), ("away", "away")])
    formation = serializers.CharField(required=False, allow_blank=True)
    is_confirmed = serializers.BooleanField(required=True)
    published_at = serializers.DateTimeField(required=False, allow_null=True)
    starters = ManualLineupPlayerInputSerializer(many=True)
    bench = ManualLineupPlayerInputSerializer(many=True)


 
