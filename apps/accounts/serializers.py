from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source="profile.gender")
    phone_number = PhoneNumberField(source="profile.phone_number")
    profile_photo = serializers.ImageField(source="profile.profile_photo")
    country = CountryField(source="profile.country")
    city = serializers.CharField(source="profile.city")
    first_name = serializers.SerializerMethodField(required=False)
    last_name = serializers.SerializerMethodField(required=False)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "gender",
            "phone_number",
            "profile_photo",
            "country",
            "city",
        )

    def get_first_name(self, obj) -> str:
        return obj.first_name.title()

    def get_last_name(self, obj) -> str:
        return obj.last_name.title()

    def get_full_name(self, obj) -> str:
        return obj.get_fullname


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")

    def create(self, validated_data):
        user = super().create(validated_data)
        user.is_active = True
        user.save()
        return user


class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    id_token = serializers.CharField(required=False)
    access_token = serializers.CharField(required=False)
    auth_code = serializers.CharField(required=False)

    def validate(self, attrs):
        if not any(
            [
                attrs.get("code"),
                attrs.get("id_token"),
                attrs.get("access_token"),
                attrs.get("auth_code"),
            ]
        ):
            raise serializers.ValidationError(
                "At least one of: code, id_token, access_token, or auth_code is required"
            )
        return attrs


class GoogleAuthResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
    is_new_user = serializers.BooleanField()
    expires_in = serializers.DateTimeField()
