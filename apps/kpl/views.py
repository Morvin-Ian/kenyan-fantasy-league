import logging
import csv
import io
import logging.config

from django.core.cache import cache
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.kpl.models import (
    Fixture,
    FixtureLineup,
    FixtureLineupPlayer,
    Player,
    Standing,
    Team,
)
from apps.kpl.services import upsert_fixture_lineup
from apps.kpl.tasks.fixtures import find_team, find_player
from config.settings import base

from .serializers import (
    FixtureLineupDetailSerializer,
    FixtureSerializer,
    PlayerBulkUploadSerializer,
    PlayerSerializer,
    StandingSerializer,
    TeamSerializer,
)

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


class TeamViewSet(ReadOnlyModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.filter(is_relegated=False)
    permission_classes = [IsAuthenticated]


class StandingViewSet(ReadOnlyModelViewSet):
    serializer_class = StandingSerializer
    queryset = Standing.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        page_number = request.query_params.get("page", 1)
        cache_key = f"standings_list_page_{page_number}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, paginated_response.data, timeout=86400)
            return Response(paginated_response.data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=86400)
        return Response(data)


class FixtureViewSet(ReadOnlyModelViewSet):
    serializer_class = FixtureSerializer
    queryset = Fixture.objects.all()
    lookup_field = "id"
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, "action", None) == "list":
            return qs.filter(gameweek__is_active=True)
        return qs

    def get_permissions(self):
        if getattr(self.request, "method", "").upper() == "POST" and getattr(
            self, "action", None
        ) in ["lineups", "upload_lineup_csv"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["get"], url_path="lineups")
    def lineups(self, request, id=None):
        fixture = self.get_object()
        if request.method == "GET":
            qs = (
                FixtureLineup.objects.filter(fixture=fixture)
                .select_related("team")
                .prefetch_related("players__player")
            )
            serializer = FixtureLineupDetailSerializer(qs, many=True)
            return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="upload-lineup-csv")
    def upload_lineup_csv(self, request):
        csv_file = request.FILES.get("file")
        fixture_id = request.data.get("fixture_id")
        team_id = request.data.get("team_id")
        side = request.data.get("side", None)

        if not csv_file or not fixture_id or not team_id:
            return Response(
                {"error": "file, fixture_id, and team_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not csv_file.name.endswith(".csv"):
            return Response(
                {"error": "Invalid file type. Please upload a CSV file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fixture = Fixture.objects.get(id=fixture_id)
        except Fixture.DoesNotExist:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response(
                {"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
        except Exception as e:
            return Response(
                {"error": f"Could not read CSV: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        players_to_add = []
        errors = []

        for i, row in enumerate(reader):
            name = row.get("name")
            position = row.get("position")

            if not name or not position:
                errors.append({"index": i, "error": "Missing name or position"})
                continue

            player = Player.objects.filter(name__iexact=name, team=team).first()
            if not player:
                errors.append(
                    {"index": i, "name": name, "error": "Player not found in team"}
                )
                continue

            players_to_add.append(
                {"player": player, "position": position, "order_index": i + 1}
            )

        if not players_to_add:
            return Response(
                {"error": "No valid players found in CSV.", "details": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            lineup, created = FixtureLineup.objects.get_or_create(
                fixture=fixture,
                team=team,
                defaults={
                    "side": side
                    or (
                        "home"
                        if fixture.home_team == team
                        else "away" if fixture.away_team == team else None
                    ),
                    "is_confirmed": True,
                    "source": "csv_upload",
                },
            )

            if not lineup.side:
                return Response(
                    {
                        "error": "Could not determine lineup side. Please provide 'side'."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            lineup.players.all().delete()

            lineup_players = [
                FixtureLineupPlayer(
                    lineup=lineup,
                    player=p["player"],
                    position=p["position"],
                    order_index=p["order_index"],
                    is_bench=False,
                )
                for p in players_to_add
            ]
            FixtureLineupPlayer.objects.bulk_create(lineup_players)

        serializer = FixtureLineupDetailSerializer(lineup)
        return Response(
            {
                "lineup": serializer.data,
                "created_count": len(players_to_add),
                "errors": errors,
            },
            status=status.HTTP_201_CREATED,
        )


class PlayerViewSet(ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.filter(team__is_relegated=False)
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser]

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "bulk_upload",
        ]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "bulk_upload":
            return PlayerBulkUploadSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        page_number = request.query_params.get("page", 1)
        team_id = request.query_params.get("team_id", "")
        cache_key = f"players_active_list_page_{page_number}_team_{team_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()

        if team_id:
            queryset = queryset.filter(team_id=team_id)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, paginated_response.data, timeout=172800)
            return Response(paginated_response.data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=172800)
        return Response(data)

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request):
        csv_file = request.FILES.get("file")

        if not csv_file:
            return Response(
                {"error": "No file uploaded. Please upload a CSV file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not csv_file.name.endswith(".csv"):
            return Response(
                {"error": "Invalid file type. Please upload a CSV file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
        except Exception as e:
            return Response(
                {"error": f"Could not read CSV file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_players = []
        updated_players = []
        errors = []

        with transaction.atomic():
            for i, row in enumerate(reader):
                try:
                    name = row.get("name")
                    team_name = row.get("team")
                    position = row.get("position")
                    jersey_number = row.get("jersey")
                    age = row.get("age")
                    current_value = row.get("value")

                    if not all([name, team_name, position]):
                        errors.append(
                            {
                                "index": i,
                                "error": "Missing one or more required fields.",
                            }
                        )
                        continue

                    try:
                        jersey_number = int(jersey_number) if jersey_number else None
                        age = int(age) if age else None
                        current_value = float(current_value) if current_value else 5.0
                    except ValueError:
                        errors.append(
                            {
                                "index": i,
                                "name": name,
                                "error": "Invalid data type for jersey_number, age, or current_value",
                            }
                        )
                        continue

                    team = Team.objects.filter(name=team_name).first()
                    if not team:
                        errors.append(
                            {
                                "index": i,
                                "name": name,
                                "error": f"Team '{team_name}' not found",
                            }
                        )
                        continue

                    existing_player = find_player(name)

                    if existing_player:
                        updated_fields = []
                        if existing_player.team != team:
                            existing_player.team = team
                            updated_fields.append("team")
                        if existing_player.position != position:
                            existing_player.position = position
                            updated_fields.append("position")
                        if existing_player.jersey_number != jersey_number:
                            existing_player.jersey_number = jersey_number
                            updated_fields.append("jersey_number")
                        if existing_player.age != age:
                            existing_player.age = age
                            updated_fields.append("age")
                        if existing_player.current_value != current_value:
                            existing_player.current_value = current_value
                            updated_fields.append("current_value")

                        if updated_fields:
                            existing_player.save(update_fields=updated_fields)
                            updated_players.append(
                                {"name": name, "updated_fields": updated_fields}
                            )
                        else:
                            continue
                    else:
                        player = Player.objects.create(
                            name=name,
                            team=team,
                            position=position,
                            jersey_number=jersey_number,
                            age=age,
                            current_value=current_value,
                        )
                        created_players.append(player)

                except Exception as e:
                    errors.append(
                        {
                            "index": i,
                            "name": row.get("name", "Unknown"),
                            "error": str(e),
                        }
                    )

        # Clear cache after changes
        cache.delete_many(cache.keys("players_active_list_*"))

        response_data = {
            "created_count": len(created_players),
            "updated_count": len(updated_players),
            "error_count": len(errors),
            "created_players": PlayerSerializer(created_players, many=True).data,
            "updated_players": updated_players,
            "errors": errors,
        }

        if errors and not created_players and not updated_players:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        elif errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response(response_data, status=status.HTTP_201_CREATED)
