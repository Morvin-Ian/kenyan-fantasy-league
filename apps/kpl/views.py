from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import TeamSerializer, StandingSerializer, FixtureSerializer, PlayerSerializer
from apps.kpl.models import Team, Standing, Fixture, Player

class TeamViewSet(ReadOnlyModelViewSet): 
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    permission_classes = [IsAuthenticated]

class StandingViewSet(ReadOnlyModelViewSet): 
    serializer_class = StandingSerializer
    queryset = Standing.objects.all()
    permission_classes = [IsAuthenticated]

class FixtureViewSet(ReadOnlyModelViewSet): 
    serializer_class = FixtureSerializer
    queryset = Fixture.objects.all()
    permission_classes = [IsAuthenticated]

class PlayerViewSet(ReadOnlyModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    permission_classes = [IsAuthenticated]
