from django.urls import path

from .views import GetProfileAPIView, UpdateProfileAPIView

urlpatterns = [
    path("", GetProfileAPIView.as_view(), name="get_profile"),
    path("update/<uuid:uuid>/", UpdateProfileAPIView.as_view(), name="update_profile"),
]
