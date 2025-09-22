from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FantasyPlayerViewSet, 
    FantasyTeamViewSet, 
    PlayerPerformanceViewSet, 
    GameweekViewSet
)

router = DefaultRouter()
router.register(r"teams", FantasyTeamViewSet, basename="fantasy-teams")
router.register(r"players", FantasyPlayerViewSet, basename="fantasy-players")
router.register(r'performance', PlayerPerformanceViewSet, basename='performance')
router.register(r"gameweek", GameweekViewSet, basename="gameweek")

urlpatterns = [
    path("", include(router.urls)),
]
