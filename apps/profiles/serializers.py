from django_countries.serializer_fields import CountryField
from rest_framework import fields, serializers

from apps.profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", read_only=True, required=False
    )
    last_name = serializers.CharField(
        source="user.last_name", read_only=True, required=False
    )
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    country = CountryField(name_only=True)
    profile_photo = serializers.SerializerMethodField(read_only=True) 

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "profile_photo",
            "gender",
            "country",
            "city",
        )

    def get_full_name(self, obj):
        first_name = obj.user.first_name
        last_name = obj.user.last_name

        if not first_name or not last_name:
            return None

        return f"{first_name.title()} {last_name.title()}"

    def get_profile_photo(self, obj):
        if obj.profile_photo:
            return obj.profile_photo.url 
        return None