from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FantasyTeamViewSet


urlpatterns = [
    path("teams/", FantasyTeamViewSet.as_view({"get": "list"}), name="fantasy-team-list"),
    path("teams/<uuid:pkid>/", FantasyTeamViewSet.as_view({"get": "retrieve"}), name="fantasy-team-detail"),
]   