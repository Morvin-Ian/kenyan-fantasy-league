from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from apps.utils import TimeStampedUUIDModel

User = get_user_model()


class Gender(models.TextChoices):
    MALE = "Male", _("Male")
    FEMALE = "Female", _("Female")
    OTHER = "Other", _("Other")


class Profile(TimeStampedUUIDModel):
    user = models.OneToOneField(User, related_name="fpl_manager", on_delete=models.CASCADE)
    phone_number = PhoneNumberField(
        verbose_name=_("Phone Number"), max_length=30, blank=True, null=True
    )
    
    team_name = models.CharField(
        verbose_name=_("Team Name"), max_length=100, blank=False, null=False
    )
    profile_photo = models.ImageField(default="/default.png")
    gender = models.CharField(
        verbose_name=_("Gender"),
        choices=Gender.choices,
        default=Gender.OTHER,
        max_length=20,
    )
    country = CountryField(
        verbose_name=_("Country"), default="KE", blank=False, null=False
    )
    city = models.CharField(
        verbose_name=_("City"),
        max_length=180,
        default="Nairobi",
        blank=False,
        null=False,
    )
    total_points = models.IntegerField(
        verbose_name=_("Total Points"), default=0
    )
    transfers_made = models.IntegerField(
        verbose_name=_("Transfers Made"), default=0
    )
    current_rank = models.IntegerField(
        verbose_name=_("Current Rank"), null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.username}'s FPL Manager Profile"