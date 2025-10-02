import logging
import csv
import io
import logging.config

from django.core.cache import cache
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
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
from apps.fantasy.models import PlayerPerformance
from apps.kpl.tasks.fixtures import find_player
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
        fixture = Fixture.objects.get(id=request.data.get("fixture_id"))
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
        from apps.fantasy.tasks.player_performance import (
            update_complete_player_performance,
        )

        csv_file = request.FILES.get("file")
        fixture_id = request.data.get("fixture_id")
        team_id = request.data.get("team_id")
        side = request.data.get("side", None)
        auto_update_performance = (
            request.data.get("auto_update_performance", "true").lower() == "true"
        )

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
            fixture = Fixture.objects.select_related(
                "home_team", "away_team", "gameweek"
            ).get(id=fixture_id)
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
            is_bench = row.get("is_bench", "").lower() in ["true", "1", "yes"]
            minutes_played = int(row.get("minutes_played", 90 if not is_bench else 0))

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
                {
                    "player": player,
                    "position": position,
                    "order_index": i + 1,
                    "is_bench": is_bench,
                    "minutes_played": minutes_played,
                }
            )

        if not players_to_add:
            return Response(
                {"error": "No valid players found in CSV.", "details": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        performance_count = 0

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
                    is_bench=p["is_bench"],
                )
                for p in players_to_add
            ]
            FixtureLineupPlayer.objects.bulk_create(lineup_players)

            # Update player performances if both lineups are uploaded
            if auto_update_performance:
                try:
                    home_lineup_exists = fixture.lineups.filter(
                        team=fixture.home_team
                    ).exists()
                    away_lineup_exists = fixture.lineups.filter(
                        team=fixture.away_team
                    ).exists()

                    if home_lineup_exists and away_lineup_exists:
                        performance_count = update_complete_player_performance(fixture)

                except Exception as e:
                    logger.error(f"Error updating player performances: {str(e)}")
                    errors.append(
                        {
                            "type": "performance_update",
                            "error": f"Failed to update player performances: {str(e)}",
                        }
                    )

        serializer = FixtureLineupDetailSerializer(lineup)
        return Response(
            {
                "lineup": serializer.data,
                "created_count": len(players_to_add),
                "performance_updated": performance_count > 0,
                "performance_count": performance_count,
                "errors": errors,
                "message": (
                    f"Lineup uploaded successfully. "
                    f"{'Player performances updated.' if performance_count > 0 else 'Waiting for both lineups to update performances.'}"
                ),
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


class MatchEventsViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Fixture.objects.all()
    serializer_class = FixtureSerializer

    @action(detail=False, methods=["post"], url_path="update-assists")
    def update_assists(self, request, pk=None):
        """
        Update assists for players in a fixture

        Request body:
        {
            "assists": [
                {"player_name": "John Doe", "team_id": "uuid", "count": 1},
                {"player_name": "Jane Smith", "team_id": "uuid", "count": 2}
            ]
        }
        """
        try:
            fixture = Fixture.objects.get(id=request.data.get("fixture_id"))
        except Fixture.DoesNotExist:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        assists_data = request.data.get("assists", [])

        if not assists_data:
            return Response(
                {"error": "assists list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_players = []
        errors = []

        with transaction.atomic():
            for assist_data in assists_data:
                player_name = assist_data.get("player_name", "").strip()
                team_id = assist_data.get("team_id")
                count = assist_data.get("count", 1)

                if not player_name or not team_id:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error": "player_name and team_id are required",
                        }
                    )
                    continue

                try:
                    team = Team.objects.get(id=team_id)
                    player = find_player(player_name)

                    if not player:
                        errors.append(
                            {
                                "player_name": player_name,
                                "error": f"Player not found in team {team.name}",
                            }
                        )
                        continue

                    performance, created = PlayerPerformance.objects.get_or_create(
                        player=player,
                        fixture=fixture,
                        gameweek=fixture.gameweek,
                        defaults={"assists": count},
                    )

                    if not created:
                        performance.assists += count

                    performance.fantasy_points = self._calculate_fantasy_points(
                        performance
                    )
                    performance.save()

                    updated_players.append(
                        {
                            "player_name": player.name,
                            "team": team.name,
                            "assists": performance.assists,
                            "fantasy_points": performance.fantasy_points,
                        }
                    )

                except Team.DoesNotExist:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error": f"Team with id {team_id} not found",
                        }
                    )
                except Exception as e:
                    errors.append({"player_name": player_name, "error": str(e)})

        return Response(
            {
                "success": True,
                "updated_count": len(updated_players),
                "updated_players": updated_players,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="update-cards")
    def update_cards(self, request, pk=None):
        """
        Request body:
        {
            "fixture_id":"uuid",
            "yellow_cards": [
                {"player_name": "John Doe", "team_id": "uuid", "count": 1}
            ],
            "red_cards": [
                {"player_name": "Bob Wilson", "team_id": "uuid", "count": 1}
            ]
        }
        """
        try:
            fixture = Fixture.objects.get(id=request.data.get("fixture_id"))
        except Fixture.DoesNotExist:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        yellow_cards = request.data.get("yellow_cards", [])
        red_cards = request.data.get("red_cards", [])

        updated_players = []
        errors = []

        with transaction.atomic():
            for card_data in yellow_cards:
                result = self._process_card(
                    fixture, card_data, "yellow_cards", "yellow"
                )
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

            for card_data in red_cards:
                result = self._process_card(fixture, card_data, "red_cards", "red")
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

        return Response(
            {
                "success": True,
                "updated_count": len(updated_players),
                "updated_players": updated_players,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="update-substitutions")
    def update_substitutions(self, request, pk=None):
        """
        Request body:
        {
            "fixture_id":"uuid",
            "substitutions": [
                {
                    "player_out": "John Doe",
                    "player_in": "Mike Johnson",
                    "team_id": "uuid",
                    "minute": 65
                }
            ]
        }
        """
        try:
            fixture = Fixture.objects.get(id=request.data.get("fixture_id"))
        except Fixture.DoesNotExist:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        substitutions = request.data.get("substitutions", [])

        if not substitutions:
            return Response(
                {"error": "substitutions list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_players = []
        errors = []

        with transaction.atomic():
            for sub_data in substitutions:
                player_out_name = sub_data.get("player_out", "").strip()
                player_in_name = sub_data.get("player_in", "").strip()
                team_id = sub_data.get("team_id")
                minute = sub_data.get("minute", 0)

                if not all([player_out_name, player_in_name, team_id]):
                    errors.append(
                        {"error": "player_out, player_in, and team_id are required"}
                    )
                    continue

                try:
                    team = Team.objects.get(id=team_id)

                    player_out = find_player(player_out_name)

                    if player_out:
                        perf_out, _ = PlayerPerformance.objects.get_or_create(
                            player=player_out,
                            fixture=fixture,
                            gameweek=fixture.gameweek,
                            defaults={"minutes_played": minute},
                        )
                        perf_out.minutes_played = minute
                        perf_out.fantasy_points = self._calculate_fantasy_points(
                            perf_out
                        )
                        perf_out.save()

                        updated_players.append(
                            {
                                "player_name": player_out.name,
                                "team": team.name,
                                "status": "substituted_out",
                                "minutes_played": minute,
                                "fantasy_points": perf_out.fantasy_points,
                            }
                        )
                    else:
                        errors.append(
                            {
                                "player_name": player_out_name,
                                "error": f"Player not found in team {team.name}",
                            }
                        )

                    player_in = find_player(player_in_name)

                    if player_in:
                        minutes_in = 90 - minute  # Minutes played after coming on
                        perf_in, _ = PlayerPerformance.objects.get_or_create(
                            player=player_in,
                            fixture=fixture,
                            gameweek=fixture.gameweek,
                            defaults={"minutes_played": minutes_in},
                        )
                        perf_in.minutes_played = minutes_in
                        perf_in.fantasy_points = self._calculate_fantasy_points(perf_in)
                        perf_in.save()

                        updated_players.append(
                            {
                                "player_name": player_in.name,
                                "team": team.name,
                                "status": "substituted_in",
                                "minutes_played": minutes_in,
                                "fantasy_points": perf_in.fantasy_points,
                            }
                        )
                    else:
                        errors.append(
                            {
                                "player_name": player_in_name,
                                "error": f"Player not found in team {team.name}",
                            }
                        )

                except Team.DoesNotExist:
                    errors.append({"error": f"Team with id {team_id} not found"})
                except Exception as e:
                    errors.append({"error": str(e)})

        return Response(
            {
                "success": True,
                "updated_count": len(updated_players),
                "updated_players": updated_players,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="update-minutes")
    def update_minutes(self, request, pk=None):
        """
        Request body:
        {
            "minutes": [
                {"player_name": "John Doe", "team_id": "uuid", "minutes_played": 90},
                {"player_name": "Jane Smith", "team_id": "uuid", "minutes_played": 65}
            ]
        }
        """
        try:
            fixture = Fixture.objects.get(id=request.data.get("fixture_id"))
        except Fixture.DoesNotExist:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        minutes_data = request.data.get("minutes", [])

        if not minutes_data:
            return Response(
                {"error": "minutes list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_players = []
        errors = []

        with transaction.atomic():
            for minute_data in minutes_data:
                player_name = minute_data.get("player_name", "").strip()
                team_id = minute_data.get("team_id")
                minutes_played = minute_data.get("minutes_played", 0)

                if not player_name or not team_id:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error": "player_name and team_id are required",
                        }
                    )
                    continue

                try:
                    team = Team.objects.get(id=team_id)
                    player = find_player(player_name)

                    if not player:
                        errors.append(
                            {
                                "player_name": player_name,
                                "error": f"Player not found in team {team.name}",
                            }
                        )
                        continue

                    performance, _ = PlayerPerformance.objects.get_or_create(
                        player=player,
                        fixture=fixture,
                        gameweek=fixture.gameweek,
                        defaults={"minutes_played": minutes_played},
                    )

                    performance.minutes_played = minutes_played
                    performance.fantasy_points = self._calculate_fantasy_points(
                        performance
                    )
                    performance.save()

                    updated_players.append(
                        {
                            "player_name": player.name,
                            "team": team.name,
                            "minutes_played": minutes_played,
                            "fantasy_points": performance.fantasy_points,
                        }
                    )

                except Team.DoesNotExist:
                    errors.append(
                        {
                            "player_name": player_name,
                            "error": f"Team with id {team_id} not found",
                        }
                    )
                except Exception as e:
                    errors.append({"player_name": player_name, "error": str(e)})

        return Response(
            {
                "success": True,
                "updated_count": len(updated_players),
                "updated_players": updated_players,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="update-goalkeeper-stats")
    def update_goalkeeper_stats(self, request, pk=None):
        """
        Request body:
        {
            "saves": [
                {"player_name": "GK Name", "team_id": "uuid", "count": 6}
            ],
            "penalties_saved": [
                {"player_name": "GK Name", "team_id": "uuid", "count": 1}
            ],
            "penalties_missed": [
                {"player_name": "Player Name", "team_id": "uuid", "count": 1}
            ]
        }
        """
        try:
            fixture = Fixture.objects.get(id=request.data.get("fixture_id"))
        except Fixture.DoesNotExist:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        saves = request.data.get("saves", [])
        penalties_saved = request.data.get("penalties_saved", [])
        penalties_missed = request.data.get("penalties_missed", [])

        updated_players = []
        errors = []

        with transaction.atomic():
            for stat_data in saves:
                result = self._process_stat(fixture, stat_data, "saves")
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

            for stat_data in penalties_saved:
                result = self._process_stat(fixture, stat_data, "penalties_saved")
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

            for stat_data in penalties_missed:
                result = self._process_stat(fixture, stat_data, "penalties_missed")
                if result.get("success"):
                    updated_players.append(result["data"])
                else:
                    errors.append(result["error"])

        return Response(
            {
                "success": True,
                "updated_count": len(updated_players),
                "updated_players": updated_players,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )

    def _process_card(self, fixture, card_data, field_name, card_type):
        player_name = card_data.get("player_name", "").strip()
        team_id = card_data.get("team_id")
        count = card_data.get("count", 1)

        if not player_name or not team_id:
            return {
                "success": False,
                "error": {
                    "player_name": player_name,
                    "error": "player_name and team_id are required",
                },
            }

        try:
            team = Team.objects.get(id=team_id)
            player = find_player(player_name)

            if not player:
                return {
                    "success": False,
                    "error": {
                        "player_name": player_name,
                        "error": f"Player not found in team {team.name}",
                    },
                }

            performance, created = PlayerPerformance.objects.get_or_create(
                player=player,
                fixture=fixture,
                gameweek=fixture.gameweek,
                defaults={field_name: count},
            )

            if not created:
                current_value = getattr(performance, field_name)
                setattr(performance, field_name, current_value + count)

            performance.fantasy_points = self._calculate_fantasy_points(performance)
            performance.save()

            return {
                "success": True,
                "data": {
                    "player_name": player.name,
                    "team": team.name,
                    "card_type": card_type,
                    field_name: getattr(performance, field_name),
                    "fantasy_points": performance.fantasy_points,
                },
            }

        except Team.DoesNotExist:
            return {
                "success": False,
                "error": {
                    "player_name": player_name,
                    "error": f"Team with id {team_id} not found",
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": {"player_name": player_name, "error": str(e)},
            }

    def _process_stat(self, fixture, stat_data, field_name):
        player_name = stat_data.get("player_name", "").strip()
        team_id = stat_data.get("team_id")
        count = stat_data.get("count", 0)

        if not player_name or not team_id:
            return {
                "success": False,
                "error": {
                    "player_name": player_name,
                    "error": "player_name and team_id are required",
                },
            }

        try:
            team = Team.objects.get(id=team_id)
            player = find_player(player_name)
            if not player:
                return {
                    "success": False,
                    "error": {
                        "player_name": player_name,
                        "error": f"Player not found in team {team.name}",
                    },
                }

            performance, created = PlayerPerformance.objects.get_or_create(
                player=player,
                fixture=fixture,
                gameweek=fixture.gameweek,
                defaults={field_name: count},
            )

            if not created:
                current_value = getattr(performance, field_name)
                setattr(performance, field_name, current_value + count)

            performance.fantasy_points = self._calculate_fantasy_points(performance)
            performance.save()

            return {
                "success": True,
                "data": {
                    "player_name": player.name,
                    "team": team.name,
                    "stat_type": field_name,
                    field_name: getattr(performance, field_name),
                    "fantasy_points": performance.fantasy_points,
                },
            }

        except Team.DoesNotExist:
            return {
                "success": False,
                "error": {
                    "player_name": player_name,
                    "error": f"Team with id {team_id} not found",
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": {"player_name": player_name, "error": str(e)},
            }

    def _calculate_fantasy_points(self, performance):
        position = performance.player.position
        points = 0

        if performance.minutes_played > 0:
            points += 1
        if performance.minutes_played >= 60:
            points += 1

        if position == "GKP":
            points += performance.goals_scored * 6
        elif position == "DEF":
            points += performance.goals_scored * 6
        elif position == "MID":
            points += performance.goals_scored * 5
        else:
            points += performance.goals_scored * 4

        points += performance.assists * 3

        if position in ["GKP", "DEF"]:
            points += performance.clean_sheets * 4
        elif position == "MID":
            points += performance.clean_sheets * 1

        if position == "GKP":
            points += performance.saves // 3

        points += performance.penalties_saved * 5
        points -= performance.penalties_missed * 2
        points -= performance.own_goals * 2
        points -= performance.yellow_cards * 1
        points -= performance.red_cards * 3

        return points
