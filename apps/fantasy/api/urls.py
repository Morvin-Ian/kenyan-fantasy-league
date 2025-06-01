from rest_framework.routers import DefaultRouter
from .views import FantasyTeamViewSet

router = DefaultRouter()
router.register(r'teams', FantasyTeamViewSet, basename='fantasy-teams')
urlpatterns = router.urls
