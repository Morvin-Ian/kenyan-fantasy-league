from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication


from apps.fantasy.models import FantasyTeam
from .serializers import FantasyTeamSerializer
from util.messages.handle_messages import success_response
from util.errors.exception_handler import CustomInternalServerError

class CustomViewset(ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTStatelessUserAuthentication]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.create(serializer.validated_data)
            data = self.get_serializer(instance).data
            response = success_response(status_code=status.HTTP_200_OK, message_code="upload_data",
                                        message={"message": "Created successfully", "data": data})
            return Response(response, status=status.HTTP_201_CREATED)
        except CustomInternalServerError as api_exec:
            raise api_exec
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            response = success_response(status_code=status.HTTP_200_OK, message_code="get_data", message={"data": data})
            return Response(data=response)
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance:
                raise CustomInternalServerError(
                    message="Resource not found.",
                    code="not_found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            content_type = request.content_type.split(';')[0].strip()

            cleaned_data: dict = {}

            if content_type == 'application/json':
                cleaned_data = request.data
            elif content_type == 'multipart/form-data':
                for key, value in request.data.items():
                    if isinstance(value, list) and len(value) == 1 and not isinstance(value[0], (
                            InMemoryUploadedFile, TemporaryUploadedFile)):
                        cleaned_data[key] = value[0]
                    else:
                        cleaned_data[key] = value
                for key, file in request.FILES.items():
                    cleaned_data[key] = file
            else:
                raise CustomInternalServerError(
                    message="Unsupported content type",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=request.data)
            updated_instance = serializer.update(instance, cleaned_data)
            data = self.get_serializer(updated_instance).data

            message = "Resource updated successfully"
            response = success_response(status_code=status.HTTP_200_OK, message_code="update_success",
                                        message={"message": message, "data": data})
            return Response(data=response, status=status.HTTP_200_OK)
        except CustomInternalServerError as api_exec:
            raise api_exec
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            response_data = success_response(status_code=status.HTTP_204_NO_CONTENT, message_code="delete_success",
                                             message="Deleted successfully.")
            return Response(data=response_data, status=status.HTTP_200_OK)

        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class FantasyTeamViewSet(CustomViewset):
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    
    @action(detail=False, methods=["get"], url_path="user-team")
    def get_user_team(self, request):
        try:
            teams = FantasyTeam.objects.filter(user=request.user)
            serializer = self.get_serializer(teams, many=True)
            response = success_response(
                status_code=200,
                message_code="get_data",
                message=serializer.data,
            )
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            raise CustomInternalServerError(
                message_code="server_error",
                message=str(e),
            )
        