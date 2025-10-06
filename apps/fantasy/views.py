from django.db.models import Count, Q, Sum
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from apps.fantasy.models import FantasyPlayer, FantasyTeam, PlayerPerformance
from apps.kpl.models import Gameweek, Player

from .serializers import (
    FantasyPlayerSerializer,
    FantasyTeamSerializer,
    PlayerPerformanceSerializer,
)
from .services.fantasy import FantasyService
from .services.gameweek_status import GameweekStatusService


class FantasyTeamViewSet(ModelViewSet):
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


    def perform_create(self, serializer):
        user = self.request.user

        if FantasyTeam.objects.filter(user=user).exists():
            raise ValidationError({"detail": "You already have a fantasy team."})

        team_name = serializer.validated_data.get("name")
        if team_name and FantasyTeam.objects.filter(name__iexact=team_name).exists():
            raise ValidationError({"detail": f"A team with the name '{team_name}' already exists."})

        try:
            with transaction.atomic():
                team = FantasyService.create_fantasy_team(user, serializer.validated_data)
                serializer.instance = team  
        except IntegrityError:
            raise ValidationError({"detail": f"A team with the name '{team_name}' already exists."})
    
    
    @action(detail=False, methods=["get"], url_path="user-team")
    def get_user_team(self, request):
        try:
            teams = FantasyTeam.objects.filter(user=request.user)
            serializer = self.get_serializer(teams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FantasyPlayerViewSet(ModelViewSet):
    queryset = FantasyPlayer.objects.all()
    serializer_class = FantasyPlayerSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    @action(detail=False, methods=["get"], url_path="team-players")
    def get_team_players(self, request):
        try:
            team = FantasyTeam.objects.filter(user=request.user)
            if team.exists():
                players = FantasyPlayer.objects.filter(fantasy_team=team.first())
                serializer = self.get_serializer(players, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "No fantasy team found for this user."},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="save-team-players")
    def save_team_players(self, request):
        try:
            starting_eleven = request.data.get("startingEleven", {})
            bench_players = request.data.get("benchPlayers", [])
            fantasy_team = FantasyTeam.objects.get(user=request.user)
            formation = request.data.get("formation", fantasy_team.formation)

            result = FantasyService.save_team_players(
                formation=formation,
                fantasy_team=fantasy_team,
                starting_eleven=starting_eleven,
                bench_players=bench_players,
            )

            return Response(
                {
                    "detail": "Team squad updated successfully.",
                    **result,
                },
                status=status.HTTP_200_OK,
            )

        except FantasyTeam.DoesNotExist:
            return Response(
                {"detail": "Fantasy team not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {
                    "detail": "Validation error occurred.",
                    "errors": e.message_dict if hasattr(e, "message_dict") else str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PlayerPerformanceViewSet(ModelViewSet):
    queryset = PlayerPerformance.objects.all()
    serializer_class = PlayerPerformanceSerializer

    @action(detail=False, methods=["get"], url_path="goals-leaderboard")
    def goals_leaderboard(self, request):
        limit = int(request.query_params.get("limit", 5))

        players_goals = (
            Player.objects.annotate(
                total_goals=Sum("performances__goals_scored"),
                total_assists=Sum("performances__assists"),
                total_appearances=Count(
                    "performances", filter=Q(performances__minutes_played__gt=0)
                ),
                total_fantasy_points=Sum("performances__fantasy_points"),
            )
            .filter(total_goals__gt=0)
            .order_by("-total_goals")[:limit]
        )

        leaderboard_data = []
        for player in players_goals:
            leaderboard_data.append(
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "team_name": player.team.name if player.team else None,
                    "total_goals": player.total_goals or 0,
                    "total_assists": player.total_assists or 0,
                    "total_appearances": player.total_appearances or 0,
                    "total_fantasy_points": player.total_fantasy_points or 0,
                    "goals_per_game": (
                        round(
                            (player.total_goals or 0) / (player.total_appearances or 1),
                            2,
                        )
                        if player.total_appearances
                        else 0
                    ),
                    "rank": len(leaderboard_data) + 1,
                }
            )

        return Response(
            {"count": len(leaderboard_data), "results": leaderboard_data},
            status=status.HTTP_200_OK,
        )


class GameweekViewSet(ModelViewSet):
    queryset = Gameweek.objects.all()

    @action(detail=False, methods=["get"], url_path="status")
    def get_gameweek_status(self, request):
        """
        Usage:
          - /api/gameweeks/status/ (active gameweek)
          - /api/gameweeks/status/?gameweek_id=5 (specific gameweek)
        """
        gameweek_id = request.query_params.get("gameweek_id")
        service = GameweekStatusService()
        data = service.get_comprehensive_gameweek_status(gameweek_id=gameweek_id)

        if "error" in data:
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)
