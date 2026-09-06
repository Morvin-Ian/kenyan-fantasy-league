"""Cache invalidation has to name the keys the endpoints actually write.

The player list caches under ``players_list_team_{team}_page_{n}`` for four
hours, and the Player signal dropped ``players_active_list_*`` — a key nothing
has ever written. So the list was never invalidated: after ``sync_players``
filled in real positions the API kept serving a squad in which everyone was a
midfielder, and picking a team could only fill the midfield. There was no Team
receiver at all, so a new jersey or badge was invisible for the same four hours.
"""

import re
from pathlib import Path

import pytest

from apps.kpl import signals as kpl_signals
from apps.kpl.models import Player, Team

REPO_ROOT = Path(__file__).resolve().parents[1]


class RecordingCache:
    """Stands in for django-redis: records what it was asked to drop."""

    def __init__(self):
        self.deleted = []
        self.patterns = []

    def delete(self, key):
        self.deleted.append(key)

    def delete_pattern(self, pattern):
        self.patterns.append(pattern)
        return 1


@pytest.fixture
def recorder(monkeypatch):
    cache = RecordingCache()
    monkeypatch.setattr(kpl_signals, "cache", cache)
    return cache


def matches(pattern: str, key: str) -> bool:
    return re.fullmatch(pattern.replace("*", ".*"), key) is not None


# The keys the read endpoints write, read straight out of the views.
def written_keys():
    source = (REPO_ROOT / "apps" / "kpl" / "views.py").read_text(encoding="utf-8")
    return set(re.findall(r'cache_key = f?"([^"]+)"', source))


@pytest.mark.django_db
def test_saving_a_player_invalidates_the_list_the_endpoint_writes(recorder):
    club = Team.objects.create(name="Cache FC", logo_url="https://example.test/l.png")
    Player.objects.create(name="Someone", team=club, position="GKP")

    dropped = recorder.patterns + recorder.deleted
    concrete = "players_list_team_abc123_page_1"
    assert any(
        matches(p, concrete) for p in dropped
    ), f"nothing invalidates {concrete!r}; dropped {dropped}"


@pytest.mark.django_db
def test_changing_a_club_invalidates_the_payloads_that_embed_it(recorder):
    """Player payloads carry the club's name and jersey."""
    Team.objects.create(name="Jersey FC", logo_url="https://example.test/l.png")

    dropped = recorder.patterns + recorder.deleted
    assert any(matches(p, "players_list_team_abc_page_1") for p in dropped)
    assert any(matches(p, "standings_list_page_1") for p in dropped)


@pytest.mark.django_db
def test_a_position_change_invalidates_the_cache(recorder):
    """The case that was actually broken: sync_players correcting a position."""
    club = Team.objects.create(name="Fix FC", logo_url="https://example.test/l.png")
    player = Player.objects.create(name="Keeper", team=club, position="MID")
    recorder.patterns.clear()
    recorder.deleted.clear()

    player.position = "GKP"
    player.position_source = "provider"
    player.save(update_fields=["position", "position_source"])

    dropped = recorder.patterns + recorder.deleted
    assert any(matches(p, "players_list_team_xyz_page_2") for p in dropped)


def test_every_cached_endpoint_key_is_covered_by_the_clear_cache_command():
    """A key nobody can drop is a key that goes stale for its whole TTL."""
    from apps.kpl.management.commands.clear_cache import GROUPS

    patterns = [p for group in GROUPS.values() for p in group]

    for template in written_keys():
        # Turn the f-string into a concrete key: players_list_team_{x}_page_{y}
        concrete = re.sub(r"\{[^}]+\}", "X", template)
        assert any(
            matches(p, concrete) for p in patterns
        ), f"{template!r} is written by a view but no clear_cache group drops it"


def test_the_signals_do_not_drop_a_key_nobody_writes():
    """The defect itself: a receiver naming a key no endpoint ever set."""
    source = (REPO_ROOT / "apps" / "kpl" / "signals.py").read_text(encoding="utf-8")
    # Both sides carry f-string placeholders; normalise them the same way.
    dropped = {
        re.sub(r"\{[^}]+\}", "X", key)
        for key in re.findall(r'drop\(\s*f?"([^"]+)"', source)
    }
    templates = {re.sub(r"\{[^}]+\}", "X", key) for key in written_keys()}
    # Keys written elsewhere than kpl/views.py.
    templates |= {
        "team_players_X",
        "goals_leaderboard_limit_X",
        "active_gameweek_number",
    }

    for pattern in dropped:
        concrete_forms = [t for t in templates if matches(pattern, t)]
        assert concrete_forms, f"{pattern!r} matches nothing any endpoint writes"
