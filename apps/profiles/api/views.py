from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from util.errors.exception_handler import CustomInternalServerError
from util.messages.handle_messages import success_response


from apps.profiles.models import Profile

from .serializers import ProfileSerializer


class GetProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = self.request.user
        user_profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(user_profile, context={"request": request})
        response = success_response(
            status_code=status.HTTP_200_OK,
            message_code="profile_retrieved",
            message=serializer.data
        )
        return Response(response, status=status.HTTP_200_OK)


class UpdateProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, uuid):
        try:
            profile = Profile.objects.filter(id=uuid).first()
    
            if profile.id != uuid:
               raise CustomInternalServerError(
                error_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid profile",
            )

            data = request.data

            user = profile.user  
            user_updated = False

            user_fields = ['username', 'email', 'last_name', 'first_name']
            for field in user_fields:
                if field in data:
                    setattr(user, field, data[field])
                    user_updated = True

            if user_updated:
                user.save()  

            serializer = ProfileSerializer(
                instance=profile, 
                data=data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                response = success_response(
                    status_code=status.HTTP_200_OK,
                    message_code="profile_updated",
                    message="Profile updated successfully",
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                raise CustomInternalServerError(
                    error_code=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                )
        except CustomInternalServerError as api_err:
            raise api_err
            
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                error_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )