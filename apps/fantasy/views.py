from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.fantasy.models import FantasyPlayer, FantasyTeam

from .serializers import FantasyPlayerSerializer, FantasyTeamSerializer
from .services import FantasyService


class FantasyTeamViewSet(ModelViewSet):
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        user = self.request.user

        if FantasyTeam.objects.filter(user=user).exists():
            raise ValidationError(
                "You already have a fantasy team.", code=status.HTTP_400_BAD_REQUEST
            )

        team_name = serializer.validated_data.get("name")
        if team_name and FantasyTeam.objects.filter(name__iexact=team_name).exists():
            raise ValidationError(
                f"A team with the name '{team_name}' already exists.",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return FantasyService.create_fantasy_team(user, serializer.validated_data)

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
