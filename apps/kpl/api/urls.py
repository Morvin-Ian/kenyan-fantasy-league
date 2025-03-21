from django.urls import path
from .views import StandingViewSet, TeamViewSet, FixtureViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"teams", TeamViewSet)
router.register(r"standings", StandingViewSet)
router.register(r"fixtures", FixtureViewSet)

urlpatterns = router.urls
