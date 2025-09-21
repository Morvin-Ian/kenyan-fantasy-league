from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.kpl.models import Fixture, FixtureLineup, Player, Standing, Team
from apps.kpl.services import upsert_fixture_lineup

from .serializers import (
    FixtureLineupDetailSerializer,
    FixtureLineupSerializer,
    FixtureSerializer,
    ManualLineupInputSerializer,
    PlayerSerializer,
    StandingSerializer,
    TeamSerializer,
)


class TeamViewSet(ReadOnlyModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.filter(is_relegated=False)
    permission_classes = [IsAuthenticated]


class StandingViewSet(ReadOnlyModelViewSet):
    serializer_class = StandingSerializer
    queryset = Standing.objects.all()
    permission_classes = [IsAuthenticated]


class FixtureViewSet(ReadOnlyModelViewSet):
    serializer_class = FixtureSerializer
    # Allow all fixtures for detail routes; filter to active GW in list via get_queryset
    queryset = Fixture.objects.exclude(status="postponed")
    lookup_field = "id"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, "action", None) == "list":
            return qs.filter(gameweek__is_active=True)
        return qs

    def get_permissions(self):
        if getattr(self.request, "method", "").upper() == "POST" and getattr(self, "action", None) == "lineups":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["get", "post"], url_path="lineups")
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

        # POST
        serializer = ManualLineupInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        side = data["side"]
        team = fixture.home_team if side == "home" else fixture.away_team
        lineup = upsert_fixture_lineup(
            fixture=fixture,
            team=team,
            side=side,
            source="manual",
            formation=data.get("formation"),
            is_confirmed=data.get("is_confirmed", False),
            published_at=data.get("published_at"),
            starters=data.get("starters", []),
            bench=data.get("bench", []),
        )
        out = FixtureLineupSerializer(lineup)
        return Response(out.data, status=status.HTTP_201_CREATED)


class PlayerViewSet(ReadOnlyModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.filter(team__is_relegated=False)
    permission_classes = [IsAuthenticated]
