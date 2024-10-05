from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet

router = DefaultRouter()
router.register(r'players', PlayerViewSet)

urlpatterns = [
    path('players/', include(router.urls)),
]