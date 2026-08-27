"""Regression test: CustomUserManager.create_user can never mint a privileged account.

``create_user`` used to apply ``extra_fields.setdefault("is_staff", False)`` and
``extra_fields.setdefault("is_superuser", False)`` AFTER ``self.model(**extra_fields)``
had already consumed the dict, so the lines were no-ops. A caller passing
``is_staff=True`` / ``is_superuser=True`` got a privileged account with no validation,
silently relying on the model field defaults for safety. The defaults are now applied
BEFORE construction and any privileged flag raises ValueError.
"""

import pytest

from apps.accounts.models import User


@pytest.mark.django_db
def test_create_user_defaults_to_non_privileged():
    user = User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="password",
        first_name="Reg",
        last_name="Ular",
    )

    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.is_active is True


@pytest.mark.django_db
def test_create_user_rejects_staff_flag():
    with pytest.raises(ValueError):
        User.objects.create_user(
            username="wannabe-staff",
            email="wannabe-staff@example.com",
            password="password",
            is_staff=True,
        )


@pytest.mark.django_db
def test_create_user_rejects_superuser_flag():
    with pytest.raises(ValueError):
        User.objects.create_user(
            username="wannabe-superuser",
            email="wannabe-superuser@example.com",
            password="password",
            is_superuser=True,
        )


@pytest.mark.django_db
def test_create_superuser_still_works():
    user = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password",
        first_name="Ad",
        last_name="Min",
    )

    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.is_active is True
