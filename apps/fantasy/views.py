from django.db.models import Count, Q, Sum
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db import IntegrityError, transaction

from apps.fantasy.models import (
    FantasyPlayer,
    FantasyTeam,
    PlayerPerformance,
    TeamSelection,
)
from apps.kpl.models import Gameweek, Player

from .serializers import (
    FantasyPlayerSerializer,
    FantasyTeamSerializer,
    PlayerPerformanceSerializer,
    TeamSelectionSerializer,
)
from .services.fantasy import FantasyService
from .services.gameweek_status import GameweekStatusService
from .services.team_service import TeamOfTheWeekService


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
            raise ValidationError(
                {"detail": f"A team with the name '{team_name}' already exists."}
            )

        try:
            with transaction.atomic():
                team = FantasyService.create_fantasy_team(
                    user, serializer.validated_data
                )
                serializer.instance = team
        except IntegrityError:
            raise ValidationError(
                {"detail": f"A team with the name '{team_name}' already exists."}
            )

    @action(detail=False, methods=["get"], url_path="user-team")
    def get_user_team(self, request):
        try:
            teams = FantasyTeam.objects.filter(user=request.user)
            
            # Get requested gameweek if provided
            gameweek_number = request.query_params.get("gameweek")
            requested_gameweek = None
            
            if gameweek_number:
                try:
                    requested_gameweek = Gameweek.objects.get(number=gameweek_number)
                except Gameweek.DoesNotExist:
                    return Response(
                        {"detail": f"Gameweek {gameweek_number} not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Pass gameweek context to serializer
            serializer = self.get_serializer(
                teams, 
                many=True,
                context={'requested_gameweek': requested_gameweek}
            )
            
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

    @action(detail=False, methods=["get"], url_path="gameweek-players")
    def get_gameweek_selection(self, request):
        try:
            fantasy_team = FantasyTeam.objects.get(user=request.user)
            gameweek_number = request.query_params.get("gameweek")

            if gameweek_number:
                gameweek = Gameweek.objects.get(number=gameweek_number)
            else:
                last_selection = (
                    TeamSelection.objects.filter(fantasy_team=fantasy_team)
                    .order_by("-gameweek__number")
                    .first()
                )

                gameweek = last_selection.gameweek if last_selection else None
                if not gameweek:
                    gameweek = Gameweek.objects.filter(is_active=True).first()

            try:
                team_selection = TeamSelection.objects.get(
                    fantasy_team=fantasy_team, gameweek=gameweek
                )

                players = list(team_selection.starters.all()) + list(
                    team_selection.bench.all()
                )

                serializer = FantasyPlayerSerializer(
                    players, 
                    many=True,
                    context={'requested_gameweek': gameweek}
                )
                return Response(serializer.data, status=status.HTTP_200_OK)

            except TeamSelection.DoesNotExist:
                return Response(
                    {
                        "detail": f"No team selection found for gameweek {gameweek.number}",
                        "gameweek": gameweek.number,
                    },
                    status=status.HTTP_200_OK,
                )

        except FantasyTeam.DoesNotExist:
            return Response(
                {"detail": "Fantasy team not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Gameweek.DoesNotExist:
            return Response(
                {"detail": "Gameweek not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
    @action(detail=False, methods=["get"], url_path="available-gameweeks")
    def get_available_gameweeks(self, request):
        try:
            fantasy_team = FantasyTeam.objects.get(user=request.user)
            
            # Get gameweeks where this team has selections
            gameweeks_with_selections = Gameweek.objects.filter(
                team_selections__fantasy_team=fantasy_team
            ).distinct().order_by('-number')
            
            # Also include current/active gameweek
            active_gameweek = Gameweek.objects.filter(is_active=True).first()
            
            gameweeks_data = []
            for gw in gameweeks_with_selections:
                gameweeks_data.append({
                    'number': gw.number,
                    'name': f'Gameweek {gw.number}',
                    'is_active': gw.is_active,
                    'has_selection': True
                })
            
            # Add active gameweek if not already included
            if active_gameweek and active_gameweek not in gameweeks_with_selections:
                gameweeks_data.append({
                    'number': active_gameweek.number,
                    'name': f'Gameweek {active_gameweek.number} (Current)',
                    'is_active': True,
                    'has_selection': False
                })
            
            return Response(gameweeks_data, status=status.HTTP_200_OK)
            
        except FantasyTeam.DoesNotExist:
            return Response(
                {"detail": "Fantasy team not found."}, 
                status=status.HTTP_404_NOT_FOUND
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

            team_selection = TeamSelection.objects.get(id=result["team_selection_id"])
            selection_serializer = TeamSelectionSerializer(team_selection)

            return Response(
                {
                    "detail": "Team squad updated successfully.",
                    "team_selection": selection_serializer.data,
                    **{k: v for k, v in result.items() if k != "team_selection_id"},
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
        from django.core.cache import cache
        
        limit = int(request.query_params.get("limit", 5))
        cache_key = f"goals_leaderboard_limit_{limit}"
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=["get"], url_path="gameweek-team")
    def team_of_the_week(self, request):
        gameweek_number = request.query_params.get("gameweek")
        gameweek = TeamOfTheWeekService.get_gameweek(gameweek_number)

        if not gameweek:
            return Response(
                {"detail": "No valid gameweek found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        team_data = TeamOfTheWeekService.get_team_of_the_week(gameweek)

        if not team_data:
            return Response(
                {"detail": "No performances found for this gameweek."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serialized = TeamOfTheWeekService.serialize_team(team_data, gameweek.number)
        return Response(serialized, status=status.HTTP_200_OK)


class GameweekViewSet(ModelViewSet):
    queryset = Gameweek.objects.all()

    @action(detail=False, methods=["get"], url_path="status")
    def get_gameweek_status(self, request):
        gameweek_id = request.query_params.get("gameweek_id")
        service = GameweekStatusService()
        data = service.get_comprehensive_gameweek_status(gameweek_id=gameweek_id)

        if "error" in data:
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)