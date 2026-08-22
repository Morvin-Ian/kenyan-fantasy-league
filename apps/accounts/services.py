import json
import logging
import os
from datetime import timedelta

import requests
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Handle Google OAuth token validation and user data extraction"""

    GOOGLE_TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v1/tokeninfo"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

    @staticmethod
    def get_user_info_from_token(access_token: str) -> dict:
        """Get user info from Google using access token"""
        try:
            response = requests.get(
                GoogleOAuthService.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get user info from Google: {e}")
            raise ValueError("Failed to retrieve user information from Google")

    @staticmethod
    def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
        """Exchange authorization code for tokens"""
        try:
            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            raise ValueError("Failed to exchange authorization code")

    @staticmethod
    def validate_token(id_token: str) -> dict:
        """Validate Google ID token"""
        try:
            response = requests.get(
                GoogleOAuthService.GOOGLE_TOKEN_INFO_URL,
                params={"id_token": id_token},
                timeout=10,
            )
            response.raise_for_status()
            token_info = response.json()

            if token_info.get("aud") != os.getenv("GOOGLE_CLIENT_ID"):
                raise ValueError("Token audience mismatch")

            return token_info
        except requests.RequestException as e:
            logger.error(f"Failed to validate token: {e}")
            raise ValueError("Failed to validate Google token")


class UserAuthService:
    """Handle user creation/retrieval and token generation"""

    @staticmethod
    def get_or_create_user(google_data: dict) -> tuple[User, bool]:
        """Get existing user or create new one from Google data"""
        email = google_data.get("email")

        if not email:
            raise ValueError("Email is required from Google")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "first_name": google_data.get("given_name", ""),
                "last_name": google_data.get("family_name", ""),
                "is_active": True,
            },
        )

        # Update profile if it exists (optional)
        if created:
            logger.info(f"New user created via Google OAuth: {email}")
        else:
            logger.info(f"Existing user logged in via Google OAuth: {email}")

        return user, created

    @staticmethod
    def generate_tokens(user: User) -> dict:
        """Generate JWT tokens for user"""
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "expires_in": timezone.now() + timedelta(days=1),
        }

    @staticmethod
    def prepare_user_response(user: User) -> dict:
        """Prepare user data for response"""
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "is_active": user.is_active,
        }
