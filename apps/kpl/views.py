import logging
import logging.config

from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.kpl.models import (
    Fixture,
    FixtureLineup,
    Player,
    Standing,
    Team,
)
from config.settings import base

from .serializers import (
    FixtureLineupDetailSerializer,
    FixtureSerializer,
    PlayerBulkUploadSerializer,
    PlayerSerializer,
    StandingSerializer,
    TeamSerializer,
)

from .services.lineup import LineupService
from .services.player import PlayerService
from .services.match_events import MatchEventService

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


class TeamViewSet(ReadOnlyModelViewSet):
    """ViewSet for viewing teams"""

    serializer_class = TeamSerializer
    queryset = Team.objects.filter(is_relegated=False)
    permission_classes = [IsAuthenticated]


class StandingViewSet(ReadOnlyModelViewSet):
    """ViewSet for viewing league standings with caching"""

    serializer_class = StandingSerializer
    queryset = Standing.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        page_number = request.query_params.get("page", 1)
        cache_key = f"standings_list_page_{page_number}"

        # cached_data = cache.get(cache_key)
        # if cached_data:
        #     return Response(cached_data)

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
    """ViewSet for managing fixtures and lineups"""

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
        """Get lineups for a fixture"""
        fixture = self.get_object()

        qs = (
            FixtureLineup.objects.filter(fixture=fixture)
            .select_related("team")
            .prefetch_related("players__player")
        )
        serializer = FixtureLineupDetailSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="upload-lineup-csv")
    def upload_lineup_csv(self, request):
        """Upload lineup from CSV file"""
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
            result = LineupService.upload_lineup_from_csv(
                csv_file=csv_file,
                fixture_id=fixture_id,
                team_id=team_id,
                side=side,
                auto_update_performance=auto_update_performance,
            )

            serializer = FixtureLineupDetailSerializer(result["lineup"])

            return Response(
                {
                    "lineup": serializer.data,
                    "created_count": result["created_count"],
                    "performance_updated": result["performance_updated"],
                    "performance_count": result["performance_count"],
                    "errors": result["errors"],
                    "message": (
                        f"Lineup uploaded successfully. "
                        f"{'Player performances updated.' if result['performance_count'] > 0 else 'Waiting for both lineups to update performances.'}"
                    ),
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error uploading lineup: {str(e)}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PlayerViewSet(ModelViewSet):
    """ViewSet for managing players with caching"""

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
        """List players with caching support"""
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
        """Bulk upload/update players from CSV"""
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
            result = PlayerService.bulk_upload_from_csv(csv_file)

            response_data = {
                "created_count": len(result["created_players"]),
                "updated_count": len(result["updated_players"]),
                "error_count": len(result["errors"]),
                "created_players": PlayerSerializer(
                    result["created_players"], many=True
                ).data,
                "updated_players": result["updated_players"],
                "errors": result["errors"],
            }

            if (
                result["errors"]
                and not result["created_players"]
                and not result["updated_players"]
            ):
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            elif result["errors"]:
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            else:
                return Response(response_data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error in bulk upload: {str(e)}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MatchEventsViewSet(ModelViewSet):
    """ViewSet for managing match events (assists, cards, substitutions, etc.)"""

    permission_classes = [IsAdminUser]
    queryset = Fixture.objects.all()
    serializer_class = FixtureSerializer

    def _get_fixture(self, request):
        try:
            return Fixture.objects.get(id=request.data.get("fixture_id"))
        except Fixture.DoesNotExist:
            return None

    @action(detail=False, methods=["post"], url_path="update-assists")
    def update_assists(self, request, pk=None):
        """
        Request body:
        {
            "fixture_id": "uuid",
            "assists": [
                {"player_name": "John Doe", "team_id": "uuid", "count": 1}
            ]
        }
        """
        fixture = self._get_fixture(request)
        if not fixture:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        assists_data = request.data.get("assists", [])
        if not assists_data:
            return Response(
                {"error": "assists list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = MatchEventService.update_assists(fixture, assists_data)

        return Response(
            {
                "success": True,
                "updated_count": len(result["updated_players"]),
                "updated_players": result["updated_players"],
                "errors": result["errors"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="update-cards")
    def update_cards(self, request, pk=None):
        """
        Request body:
        {
            "fixture_id": "uuid",
            "yellow_cards": [{"player_name": "John Doe", "team_id": "uuid", "count": 1}],
            "red_cards": [{"player_name": "Bob Wilson", "team_id": "uuid", "count": 1}]
        }
        """
        fixture = self._get_fixture(request)
        if not fixture:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        yellow_cards = request.data.get("yellow_cards", [])
        red_cards = request.data.get("red_cards", [])

        result = MatchEventService.update_cards(fixture, yellow_cards, red_cards)

        return Response(
            {
                "success": True,
                "updated_count": len(result["updated_players"]),
                "updated_players": result["updated_players"],
                "errors": result["errors"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="update-substitutions")
    def update_substitutions(self, request, pk=None):
        """
        Request body:
        {
            "fixture_id": "uuid",
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
        fixture = self._get_fixture(request)
        if not fixture:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        substitutions = request.data.get("substitutions", [])
        if not substitutions:
            return Response(
                {"error": "substitutions list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = MatchEventService.update_substitutions(fixture, substitutions)

        return Response(
            {
                "success": True,
                "updated_count": len(result["updated_players"]),
                "updated_players": result["updated_players"],
                "errors": result["errors"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="update-minutes")
    def update_minutes(self, request, pk=None):
        """
        Request body:
        {
            "fixture_id": "uuid",
            "minutes": [
                {"player_name": "John Doe", "team_id": "uuid", "minutes_played": 90}
            ]
        }
        """
        fixture = self._get_fixture(request)
        if not fixture:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        minutes_data = request.data.get("minutes", [])
        if not minutes_data:
            return Response(
                {"error": "minutes list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = MatchEventService.update_minutes(fixture, minutes_data)

        return Response(
            {
                "success": True,
                "updated_count": len(result["updated_players"]),
                "updated_players": result["updated_players"],
                "errors": result["errors"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="update-goalkeeper-stats")
    def update_goalkeeper_stats(self, request, pk=None):
        """
        Request body:
        {
            "fixture_id": "uuid",
            "saves": [{"player_name": "GK Name", "team_id": "uuid", "count": 6}],
            "penalties_saved": [{"player_name": "GK Name", "team_id": "uuid", "count": 1}],
            "penalties_missed": [{"player_name": "Player Name", "team_id": "uuid", "count": 1}]
        }
        """
        fixture = self._get_fixture(request)
        if not fixture:
            return Response(
                {"error": "Fixture not found."}, status=status.HTTP_404_NOT_FOUND
            )

        saves = request.data.get("saves", [])
        penalties_saved = request.data.get("penalties_saved", [])
        penalties_missed = request.data.get("penalties_missed", [])

        result = MatchEventService.update_goalkeeper_stats(
            fixture, saves, penalties_saved, penalties_missed
        )

        return Response(
            {
                "success": True,
                "updated_count": len(result["updated_players"]),
                "updated_players": result["updated_players"],
                "errors": result["errors"],
            },
            status=status.HTTP_200_OK,
        )
