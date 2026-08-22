import json
import logging
import urllib.parse

from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import GoogleAuthSerializer
from .services import GoogleOAuthService, UserAuthService

logger = logging.getLogger(__name__)


class GoogleAuthInitView(APIView):
    """Initialize Google OAuth flow by redirecting to Google's authorization page"""

    def get(self, request):
        redirect_to = request.GET.get("redirect_to", settings.FRONTEND_URL)
        origin = request.GET.get("origin", "learner")

        logger.info(
            f"GoogleAuthInitView: Creating OAuth flow with redirect_to='{redirect_to}', origin='{origin}'"
        )

        state_data = {
            "redirect_to": f"{redirect_to}/auth/callback",
            "origin": origin,
            "timestamp": timezone.now().isoformat(),
        }
        state = json.dumps(state_data)

        # Google OAuth parameters
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": f"{settings.BASE_BACKEND_URL}/api/v1/auth/google/callback/",
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }

        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
        logger.info("Redirecting to Google auth URL")
        return redirect(auth_url)


class GoogleAuthCallbackView(APIView):
    """Handle Google OAuth callback with authorization code"""

    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")
        error = request.GET.get("error")

        redirect_to = f"{settings.FRONTEND_URL}/auth/callback"
        origin = "learner"

        # Parse state to get original redirect_to and origin
        if state:
            try:
                state_data = json.loads(state)
                redirect_to = state_data.get("redirect_to", settings.FRONTEND_URL)
                origin = state_data.get("origin", "learner")
                logger.info(
                    f"Parsed state - redirect_to: {redirect_to}, origin: {origin}"
                )
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Failed to parse state '{state}': {e}")

        # Handle Google error response
        if error:
            logger.error(f"Google OAuth error: {error}")
            error_description = request.GET.get("error_description", error)
            error_url = f"{redirect_to}?auth_success=false&auth_message={urllib.parse.quote(error_description)}&origin={origin}"
            return redirect(error_url)

        # Check for authorization code
        if not code:
            logger.error("No authorization code received from Google")
            error_url = (
                f"{redirect_to}?auth_success=false&auth_message=no_code&origin={origin}"
            )
            return redirect(error_url)

        try:
            # Exchange code for tokens
            callback_uri = f"{settings.BASE_BACKEND_URL}/api/v1/auth/google/callback/"
            token_response = GoogleOAuthService.exchange_code_for_tokens(
                code, callback_uri
            )

            # Get user info from Google
            access_token = token_response.get("access_token")
            google_user_data = GoogleOAuthService.get_user_info_from_token(access_token)

            # Get or create user
            user, is_new = UserAuthService.get_or_create_user(google_user_data)

            # Generate JWT tokens
            tokens = UserAuthService.generate_tokens(user)
            user_data = UserAuthService.prepare_user_response(user)

            # Prepare response data
            response_data = {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": user_data,
                "is_new_user": is_new,
            }

            # Encode data for URL
            encoded_tokens = urllib.parse.quote(
                json.dumps(
                    {
                        "access": tokens["access"],
                        "refresh": tokens["refresh"],
                    }
                )
            )
            encoded_user = urllib.parse.quote(json.dumps(user_data))

            # Redirect to frontend with tokens and user data
            success_url = f"{redirect_to}?auth_success=true&auth_message=success&tokens={encoded_tokens}&user={encoded_user}&is_new_user={is_new}&origin={origin}"
            logger.info(
                f"Google OAuth successful for user: {user.email}, redirecting to: {redirect_to}"
            )

            return redirect(success_url)

        except ValueError as e:
            logger.error(f"Google auth validation failed: {str(e)}")
            error_url = f"{redirect_to}?auth_success=false&auth_message={urllib.parse.quote(str(e))}&origin={origin}"
            return redirect(error_url)
        except Exception as e:
            logger.error(f"Unexpected error in Google OAuth callback: {str(e)}")
            error_url = f"{redirect_to}?auth_success=false&auth_message=authentication_failed&origin={origin}"
            return redirect(error_url)


class GoogleAuthTokenView(APIView):
    """
    Alternative endpoint for frontend to exchange token directly
    Useful if frontend gets the token and wants to validate/exchange it
    """

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # If code is provided, exchange it
            if serializer.validated_data.get("code"):
                callback_uri = (
                    f"{settings.BASE_BACKEND_URL}/api/v1/auth/google/callback/"
                )
                token_response = GoogleOAuthService.exchange_code_for_tokens(
                    serializer.validated_data["code"], callback_uri
                )
                access_token = token_response.get("access_token")
            else:
                # Use provided access_token or id_token
                access_token = serializer.validated_data.get("access_token")

            # Get user info from Google
            google_user_data = GoogleOAuthService.get_user_info_from_token(access_token)

            # Get or create user
            user, is_new = UserAuthService.get_or_create_user(google_user_data)

            # Generate JWT tokens
            tokens = UserAuthService.generate_tokens(user)
            user_data = UserAuthService.prepare_user_response(user)

            response_data = {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": user_data,
                "is_new_user": is_new,
                "expires_in": tokens["expires_in"],
            }

            logger.info(f"Google auth successful for user: {user.email}")
            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(f"Google auth validation failed: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in Google auth: {str(e)}")
            return Response(
                {"detail": "Authentication failed"}, status=status.HTTP_400_BAD_REQUEST
            )
