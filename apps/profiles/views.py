from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.profiles.models import Profile
from .serializers import ProfileSerializer
from apps.kpl.tasks import players, standings, fixtures
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .services import ProfileService

User = get_user_model()


class GetProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = self.request.user
        # players.get_all_players.delay()
        # standings.get_kpl_table.delay()
        # fixtures.get_kpl_fixtures.delay()
        user_profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(user_profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, uuid):
        try:
            profile = Profile.objects.filter(id=uuid).first()
            if not profile:
                return Response(
                    {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
                )

            if profile.id != uuid:
                return Response(
                    {"detail": "Invalid profile ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            data = request.data
            user = profile.user
            user_updated = False
            user_fields = ["username", "email", "last_name", "first_name"]

            if "username" in data and data["username"] != user.username:
                if (
                    User.objects.filter(username=data["username"])
                    .exclude(id=user.id)
                    .exists()
                ):
                    return Response(
                        {"detail": "Username already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if "email" in data and data["email"] != user.email:
                if (
                    User.objects.filter(email=data["email"])
                    .exclude(id=user.id)
                    .exists()
                ):
                    return Response(
                        {"detail": "Email already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            for field in user_fields:
                if field in data:
                    setattr(user, field, data[field])
                    user_updated = True

            if user_updated:
                try:
                    user.save()
                except IntegrityError as e:
                    return Response(
                        {"detail": "Conflict updating user: " + str(e)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer = ProfileSerializer(instance=profile, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Invalid data.", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
