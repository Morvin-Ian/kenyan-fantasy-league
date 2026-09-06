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
from apps.fantasy.models import FantasyTeam

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


@override_settings(CACHES=LOCMEM_CACHE)
@pytest.mark.django_db
def test_gameweek_players_returns_not_found_when_no_gameweek_is_available(monkeypatch):
    """GET /fantasy/players/gameweek-players must not dereference a missing gameweek."""
    # The FantasyTeam post_save signal reaches past the cache for a raw Redis
    # client, which the locmem backend cannot hand out.
    # apps.fantasy.signals.drop() swallows its own cache failures now, so the
    # receivers no longer need a stand-in Redis connection to survive.

    user = User.objects.create_user(
        username="team-owner",
        email="team-owner@example.com",
        password="password",
        first_name="Team",
        last_name="Owner",
    )

    # The 404 under test is the no-active-gameweek branch, which is only
    # reached once the user has a team.
    FantasyTeam.objects.create(user=user, name="Owner XI")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/fantasy/players/gameweek-players/")

    assert response.status_code == 404
    assert response.data == {"detail": "No active gameweek found."}


@override_settings(CACHES=LOCMEM_CACHE)
@pytest.mark.django_db
@pytest.mark.parametrize("gameweek", ["invalid", "0", "-1"])
def test_gameweek_players_rejects_non_positive_or_non_numeric_gameweek(
    monkeypatch, gameweek
):
    """The optional gameweek query parameter must not reach an integer ORM field raw."""
    # apps.fantasy.signals.drop() swallows its own cache failures now, so the
    # receivers no longer need a stand-in Redis connection to survive.
    user = User.objects.create_user(
        username="team-owner",
        email="team-owner@example.com",
        password="password",
        first_name="Team",
        last_name="Owner",
    )
    FantasyTeam.objects.create(user=user, name="Owner XI")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(
        "/api/v1/fantasy/players/gameweek-players/", {"gameweek": gameweek}
    )

    assert response.status_code == 400
    assert response.data == {"detail": "Gameweek must be a positive integer."}


@override_settings(CACHES=LOCMEM_CACHE)
@pytest.mark.django_db
def test_a_failed_load_is_not_reported_as_having_no_team(monkeypatch):
    """A team that exists but cannot be serialised must not look like no team.

    The endpoint caught every exception and returned a ``{"detail": ...}`` body,
    and the client coerced any non-list body to ``[]``. So a server-side failure
    rendered the "Build Your KPL Fantasy Team!" empty state, and creating one
    then failed with "You already have a fantasy team." A pending migration
    presented exactly that way.

    The endpoint must answer with an error status, so the client can tell the
    two apart.
    """
    user = User.objects.create_user(
        username="owner",
        email="owner@example.com",
        password="password",
        first_name="Team",
        last_name="Owner",
    )
    FantasyTeam.objects.create(user=user, name="Existing XI", formation="4-4-2")

    def explode(*args, **kwargs):
        raise RuntimeError("column fantasy_teamselection.points does not exist")

    monkeypatch.setattr(
        "apps.fantasy.serializers.FantasyTeamSerializer.to_representation", explode
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/v1/fantasy/teams/user-team/")

    assert response.status_code >= 500
    # And crucially not an empty list, which is the "you have no team" answer.
    assert response.data != []
