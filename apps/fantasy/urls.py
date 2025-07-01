from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FantasyPlayerViewSet, FantasyTeamViewSet

router = DefaultRouter()
router.register(r"teams", FantasyTeamViewSet, basename="fantasy-teams")
router.register(r"players", FantasyPlayerViewSet, basename="fantasy-players")
urlpatterns = [
    path("", include(router.urls)),
]
