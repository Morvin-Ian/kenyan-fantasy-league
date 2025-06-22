from rest_framework.routers import DefaultRouter
from .views import FantasyTeamViewSet, FantasyPlayerViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'teams', FantasyTeamViewSet, basename='fantasy-teams')
router.register(r'players', FantasyPlayerViewSet, basename='fantasy-players')
urlpatterns = [
    path('', include(router.urls)),
]
