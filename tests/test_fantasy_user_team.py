"""Regression test: GET /fantasy/teams/user-team returns a list, even when empty.

``FantasyTeamViewSet.get_user_team`` answered a user with no team with
``{"detail": "No fantasy team found for this user."}`` — a dict — on HTTP 200.
The client stores that body straight into ``fantasyStore.userTeam`` (typed
``FantasyTeam[]``) and the Team page gates its three states on array shapes:
``userTeam.length > 0`` for the team view and ``userTeam.length === 0`` for the
"Build Your KPL Fantasy Team!" empty state. On a dict both are ``undefined``
comparisons that are false, so neither branch rendered and the page was blank.
The endpoint must keep its list contract so the frontend's guards work.
"""

import pytest
from django.test.utils import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import User

# The view reads/writes the default cache (Redis) directly; swap it for a
# locmem cache so the test does not need a running Redis.
LOCMEM_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-fantasy-user-team",
    }
}


@override_settings(CACHES=LOCMEM_CACHE)
@pytest.mark.django_db
def test_user_team_returns_empty_list_when_user_has_no_team():
    user = User.objects.create_user(
        username="newcomer",
        email="newcomer@example.com",
        password="password",
        first_name="New",
        last_name="Comer",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/fantasy/teams/user-team/")

    assert response.status_code == 200
    assert response.data == []
