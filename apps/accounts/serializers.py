from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from djoser.serializers import UserCreateSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source="profile.gender")
    phone_number = PhoneNumberField(source="profile.phone_number")
    profile_photo = serializers.ImageField(source="profile.profile_photo")
    country = CountryField(source="profile.country")
    city = serializers.CharField(source="profile.city")
    first_name = serializers.SerializerMethodField(required=False)
    last_name = serializers.SerializerMethodField(required=False)
    full_name = serializers.SerializerMethodField(source="get_fullname")

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


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")

    def create(self, validated_data):
        user = super().create(validated_data)
        user.is_active = True
        user.save()
        return user
