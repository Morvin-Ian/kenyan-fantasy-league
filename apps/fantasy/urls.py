from rest_framework.routers import DefaultRouter
from .views import FantasyTeamViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'teams', FantasyTeamViewSet, basename='fantasy-teams')
urlpatterns = [
    path('', include(router.urls)),
]
