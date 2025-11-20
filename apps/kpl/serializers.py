from django.db import models
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
    events_summary = serializers.SerializerMethodField(read_only=True)
    events = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Fixture
        exclude = ("pkid", "created_at", "updated_at")

    def get_is_active(self, obj):
        if obj.gameweek:
            if obj.gameweek.is_active:
                return True
        return False

    def get_lineups(self, obj):
        qs = obj.lineups.select_related("team").prefetch_related("players__player")
        return FixtureLineupDetailSerializer(qs, many=True).data

    def get_events_summary(self, obj):
        performances = obj.performances.aggregate(
            total_goals=models.Sum("goals_scored"),
            total_assists=models.Sum("assists"),
            total_yellow_cards=models.Sum("yellow_cards"),
            total_red_cards=models.Sum("red_cards"),
            total_penalties_saved=models.Sum("penalties_saved"),
            total_penalties_missed=models.Sum("penalties_missed"),
        )

        return {
            "goals": performances["total_goals"] or 0,
            "assists": performances["total_assists"] or 0,
            "yellow_cards": performances["total_yellow_cards"] or 0,
            "red_cards": performances["total_red_cards"] or 0,
            "penalties_saved": performances["total_penalties_saved"] or 0,
            "penalties_missed": performances["total_penalties_missed"] or 0,
        }

    def get_events(self, obj):
        performances = obj.performances.select_related("player", "player__team").all()
        return self._compile_events_from_performances(performances)

    def _compile_events_from_performances(self, performances):
        events = []

        for performance in performances:
            team_data = {
                "player_name": performance.player.name,
                "player_id": performance.player.id,
                "team_id": performance.player.team.id,
                "team_name": performance.player.team.name,
            }

            # Goals
            for i in range(performance.goals_scored):
                events.append(
                    {
                        **team_data,
                        "type": "goal",
                        "event_id": f"goal_{performance.id}_{i}",
                    }
                )

            # Assists
            for i in range(performance.assists):
                events.append(
                    {
                        **team_data,
                        "type": "assist",
                        "event_id": f"assist_{performance.id}_{i}",
                    }
                )

            # Yellow Cards
            for i in range(performance.yellow_cards):
                events.append(
                    {
                        **team_data,
                        "type": "yellow_card",
                        "event_id": f"yellow_{performance.id}_{i}",
                    }
                )

            # Red Cards
            for i in range(performance.red_cards):
                events.append(
                    {
                        **team_data,
                        "type": "red_card",
                        "event_id": f"red_{performance.id}_{i}",
                    }
                )

            # Penalties Saved (for goalkeepers)
            for i in range(performance.penalties_saved):
                events.append(
                    {
                        **team_data,
                        "type": "penalty_saved",
                        "event_id": f"pen_saved_{performance.id}_{i}",
                    }
                )

            # Penalties Missed
            for i in range(performance.penalties_missed):
                events.append(
                    {
                        **team_data,
                        "type": "penalty_missed",
                        "event_id": f"pen_missed_{performance.id}_{i}",
                    }
                )

        type_order = {
            "goal": 0,
            "assist": 1,
            "yellow_card": 2,
            "red_card": 3,
            "penalty_saved": 4,
            "penalty_missed": 5,
        }
        events.sort(key=lambda x: type_order.get(x["type"], 999))

        return events


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

class LineupSubmissionSerializer(serializers.Serializer):
    fixture_id = serializers.CharField(required=True)
    team_id = serializers.CharField(required=True)
    side = serializers.ChoiceField(choices=['home', 'away'], required=False)
    formation = serializers.CharField(required=True)
    starting_xi = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )
    bench_players = serializers.ListField(
        child=serializers.CharField(),
        default=list
    )

    def validate_starting_xi(self, value):
        if len(value) != 11:
            raise serializers.ValidationError("Starting XI must have exactly 11 players")
        return value

    def validate_formation(self, value):
        valid_formations = ['4-4-2', '4-3-3', '4-2-3-1', '3-5-2', '3-4-3', '5-3-2', '4-5-1']
        if value not in valid_formations:
            raise serializers.ValidationError(f"Formation must be one of {valid_formations}")
        return value