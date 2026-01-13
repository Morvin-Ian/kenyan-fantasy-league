from django.urls import path
from apps.accounts.views import (
    GoogleAuthInitView,
    GoogleAuthCallbackView,
    GoogleAuthTokenView,
)

urlpatterns = [
    path("google/login/", GoogleAuthInitView.as_view(), name="google-auth-init"),
    path("google/callback/", GoogleAuthCallbackView.as_view(), name="google-auth-callback"),
    path("google/token/", GoogleAuthTokenView.as_view(), name="google-auth-token"),
]
