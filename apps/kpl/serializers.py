from rest_framework import serializers

from apps.kpl.models import (
    Fixture,
    FixtureLineup,
    FixtureLineupPlayer,
    Player,
    Standing,
    Team,
)


class TeamSerializer(serializers.ModelSerializer):
    jersey_image = serializers.SerializerMethodField()

    class Meta:
        model = Team
        exclude = ("pkid", "created_at", "updated_at")

    def get_jersey_image(self, obj):
        if obj.jersey_image:
            return obj.jersey_image.url
        return None


class StandingSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Standing
        exclude = ("pkid", "created_at", "updated_at")


class FixtureSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    gameweek = serializers.CharField(source="gameweek.number", read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)
    lineups = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Fixture
        exclude = ("pkid", "created_at", "updated_at")

    def get_is_active(self, obj):
        if obj.gameweek:
            if obj.gameweek.is_active:
                return True
        return False

    def get_lineups(self, obj):
        """Attach lineups (home & away) with starters and bench"""
        qs = obj.lineups.select_related("team").prefetch_related("players__player")
        return FixtureLineupDetailSerializer(qs, many=True).data


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


class PlayerCreateSerializer(serializers.ModelSerializer):
    team_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Player
        fields = [
            "name",
            "team_id",
            "position",
            "jersey_number",
            "age",
            "current_value",
        ]

    def validate_team_id(self, value):
        """Validate that the team exists and is not relegated"""
        try:
            team = Team.objects.get(id=value)
            if team.is_relegated:
                raise serializers.ValidationError(
                    "Cannot add players to relegated teams"
                )
            return value
        except Team.DoesNotExist:
            raise serializers.ValidationError("Team does not exist")

    def validate_jersey_number(self, value):
        """Validate jersey number is within reasonable range"""
        if value is not None and (value < 1 or value > 99):
            raise serializers.ValidationError("Jersey number must be between 1 and 99")
        return value

    def validate(self, data):
        """Validate that jersey number is unique within the team"""
        if data.get("jersey_number"):
            existing_player = Player.objects.filter(
                team_id=data["team_id"], jersey_number=data["jersey_number"]
            ).first()

            if existing_player:
                raise serializers.ValidationError(
                    {
                        "jersey_number": f"Jersey number {data['jersey_number']} is already taken by {existing_player.name}"
                    }
                )

        return data

    def create(self, validated_data):
        team_id = validated_data.pop("team_id")
        validated_data["team_id"] = team_id
        return Player.objects.create(**validated_data)


class PlayerBulkUploadSerializer(serializers.Serializer):
    players = serializers.ListField(
        child=PlayerCreateSerializer(),
        min_length=1,
        max_length=100,
        help_text="List of players to create",
    )

    def validate_players(self, value):
        team_names = {}
        jersey_numbers = {}

        for i, player_data in enumerate(value):
            team_id = str(player_data["team_id"])
            name = player_data["name"].strip().lower()
            jersey_number = player_data.get("jersey_number")

            if team_id not in team_names:
                team_names[team_id] = {}

            if name in team_names[team_id]:
                raise serializers.ValidationError(
                    f"Duplicate player name '{player_data['name']}' found for the same team at positions {team_names[team_id][name]} and {i}"
                )
            team_names[team_id][name] = i

            if jersey_number:
                if team_id not in jersey_numbers:
                    jersey_numbers[team_id] = {}

                if jersey_number in jersey_numbers[team_id]:
                    raise serializers.ValidationError(
                        f"Duplicate jersey number '{jersey_number}' found for the same team at positions {jersey_numbers[team_id][jersey_number]} and {i}"
                    )
                jersey_numbers[team_id][jersey_number] = i

        return value
