from .models import  Profile

class ProfileService:
    @staticmethod
    def create_profile(data:dict) -> Profile:
        profile = Profile.objects.create(**data)
        return profile

    @staticmethod
    def update_profile(profile:Profile, data:dict) -> Profile:
        for key, value in data.items():
            setattr(profile, key, value)
        profile.save()
        return profile

    @staticmethod
    def delete_profile(profile:Profile) -> Profile:
        profile.delete()
        return profile
