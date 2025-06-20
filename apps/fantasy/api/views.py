from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication


from apps.fantasy.models import FantasyTeam
from .serializers import FantasyTeamSerializer

class FantasyTeamViewSet(ModelViewSet):
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    
    @action(detail=False, methods=["get"], url_path="user-team")
    def get_user_team(self, request):
        try:
            teams = FantasyTeam.objects.filter(user=request.user)
            serializer = self.get_serializer(teams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        