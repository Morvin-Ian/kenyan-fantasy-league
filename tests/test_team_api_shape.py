"""The public API must serve our own badge, never the upstream one.

``Team`` holds two badge fields: ``logo_url``, the address the scraper
downloaded from, and ``logo_image``, our cached copy. The serializer used to
``exclude`` a few housekeeping columns rather than list what it returns, so
``logo_url`` was published to every visitor. That did two bad things: it named a
third-party source in every API response and in every browser's network log,
and it made the badges break whenever that host moved its media paths.

The serializer now returns ``logo`` (the cached file) and lists its fields
explicitly, so a new model column cannot leak into the API just by existing.
"""

import pytest
from django.core.files.base import ContentFile

from apps.kpl.models import Standing, Team
from apps.kpl.serializers import StandingSerializer, TeamSerializer

UPSTREAM = "https://upstream.invalid/badges/team.png"


@pytest.fixture
def team(db):
    club = Team.objects.create(name="Example FC", logo_url=UPSTREAM)
    club.logo_image.save("example.png", ContentFile(b"not-really-a-png"), save=True)
    return club


@pytest.mark.django_db
def test_the_upstream_badge_url_is_never_serialised(team):
    data = TeamSerializer(team).data

    assert "logo_url" not in data
    assert UPSTREAM not in str(data)


@pytest.mark.django_db
def test_the_served_badge_is_our_own_media(team):
    data = TeamSerializer(team).data

    assert data["logo"].startswith("/mediafiles/")
    assert data["logo"] == team.logo_image.url


@pytest.mark.django_db
def test_a_club_with_no_cached_badge_returns_null_not_the_upstream_url(db):
    club = Team.objects.create(name="Uncached FC", logo_url=UPSTREAM)

    data = TeamSerializer(club).data

    assert data["logo"] is None
    assert UPSTREAM not in str(data)


@pytest.mark.django_db
def test_the_serializer_lists_its_fields_so_new_columns_cannot_leak(team):
    """`exclude` is what let logo_url out; an explicit allowlist is the fix."""
    assert set(TeamSerializer(team).data) == {
        "id",
        "name",
        "logo",
        "jersey_image",
        "is_relegated",
    }


@pytest.mark.django_db
def test_nested_team_payloads_are_covered_too(team):
    """Standings, fixtures and lineups all embed TeamSerializer."""
    Standing.objects.create(
        team=team,
        position=1,
        played=1,
        wins=1,
        draws=0,
        losses=0,
        goals_for=2,
        goals_against=0,
        goal_differential=2,
        points=3,
        period="2026-2027",
    )

    assert UPSTREAM not in str(StandingSerializer(Standing.objects.get()).data)
