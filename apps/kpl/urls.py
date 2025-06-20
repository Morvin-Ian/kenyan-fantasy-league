from django.urls import path
from .views import StandingViewSet, TeamViewSet, FixtureViewSet, PlayerViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"teams", TeamViewSet)
router.register(r"standings", StandingViewSet)
router.register(r"fixtures", FixtureViewSet)
router.register(r"players", PlayerViewSet)

urlpatterns = router.urls
