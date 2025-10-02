from rest_framework.routers import DefaultRouter

from .views import (
    FixtureViewSet,
    PlayerViewSet,
    StandingViewSet,
    TeamViewSet,
    MatchEventsViewSet,
)

router = DefaultRouter()
router.register(r"teams", TeamViewSet)
router.register(r"standings", StandingViewSet)
router.register(r"fixtures", FixtureViewSet)
router.register(r"players", PlayerViewSet)
router.register(r"match-events", MatchEventsViewSet, basename="match-events")
urlpatterns = router.urls


# POST 	/match-events/{id}/update-assists/	Update assists
# POST	/match-events/{id}/update-cards/	Update yellow/red cards
# POST	/match-events/{id}/update-substitutions/	Update substitutions
# POST	/match-events/{id}/update-minutes/	Bulk update minutes played
# POST	/match-events/{id}/update-goalkeeper-stats/