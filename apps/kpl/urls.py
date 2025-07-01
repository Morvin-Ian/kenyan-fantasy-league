from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import FixtureViewSet, PlayerViewSet, StandingViewSet, TeamViewSet

router = DefaultRouter()
router.register(r"teams", TeamViewSet)
router.register(r"standings", StandingViewSet)
router.register(r"fixtures", FixtureViewSet)
router.register(r"players", PlayerViewSet)

urlpatterns = router.urls
