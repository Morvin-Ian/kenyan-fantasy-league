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


@override_settings(CACHES=LOCMEM_CACHE)
@pytest.mark.django_db
def test_team_players_returns_empty_list_when_user_has_no_team():
    """GET /fantasy/players/team-players must keep the same list contract.

    ``FantasyPlayerViewSet.get_team_players`` answered a teamless user with
    ``{"detail": "No fantasy team found for this user."}`` on HTTP 200 — the
    same dict-on-200 shape that broke ``get_user_team`` and blanked the Team
    page. Both endpoints are list endpoints (the non-empty branches return
    ``many=True`` serializer data), so the empty branch must return ``[]``.
    """
    user = User.objects.create_user(
        username="newcomer",
        email="newcomer@example.com",
        password="password",
        first_name="New",
        last_name="Comer",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/fantasy/players/team-players/")

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_gameweek_players_returns_not_found_when_no_gameweek_is_available():
    """GET /fantasy/players/gameweek-players must not dereference a missing gameweek."""
    user = User.objects.create_user(
        username="team-owner",
        email="team-owner@example.com",
        password="password",
        first_name="Team",
        last_name="Owner",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/fantasy/players/gameweek-players/")

    assert response.status_code == 404
    assert response.data == {"detail": "No active gameweek found."}
