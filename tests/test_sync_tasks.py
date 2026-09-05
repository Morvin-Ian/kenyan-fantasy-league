"""Behavioural coverage for the KPL sync tasks.

The headline guarantee here is the one the previous standings task got wrong:
it called ``Standing.objects.all().delete()`` *before* parsing, so any parse
failure — a WAF challenge page, a moved column, a source redesign — left the
site with no league table at all until the next successful run. A snapshot is
now built and validated in full before anything is deleted.
"""

from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from apps.kpl.models import (
    ExternalFixtureMapping,
    ExternalTeamMapping,
    Fixture,
    Gameweek,
    Standing,
    Team,
)
from apps.kpl.scraping.exceptions import SourceUnavailable, StructureChanged
from apps.kpl.scraping.providers import primary
from apps.kpl.tasks import sync

SEASON = primary.Season(
    tournament_id="cmp0122",
    label="Kenya Premier League 2026/2027",
    start_year=2026,
    end_year=2027,
)


@pytest.fixture(autouse=True)
def pinned_season(monkeypatch):
    """Avoid a network round trip for season discovery in every test."""
    monkeypatch.setattr(sync, "current_season", lambda **kwargs: SEASON)


@pytest.fixture
def clubs(db):
    teams = {}
    for name, provider_id in [
        ("Gor Mahia FC", "clb00036"),
        ("AFC Leopards", "clb00038"),
        ("Tusker FC", "clb00035"),
    ]:
        team = Team.objects.create(name=name, logo_url="https://example.test/l.png")
        ExternalTeamMapping.objects.create(
            provider=primary.PROVIDER, provider_team_id=provider_id, team=team
        )
        teams[provider_id] = team
    return teams


def standing_row(position, provider_id, name, points):
    return primary.StandingRow(
        position=position,
        provider_team_id=provider_id,
        team_name=name,
        logo_url=None,
        played=10,
        wins=points // 3,
        draws=0,
        losses=0,
        goals_for=points,
        goals_against=0,
        goal_differential=points,
        points=points,
    )


# --------------------------------------------------------------------------- #
# Standings: never destroy the table before you can rebuild it
# --------------------------------------------------------------------------- #


@pytest.mark.django_db
def test_standings_snapshot_replaces_the_table(monkeypatch, clubs):
    monkeypatch.setattr(
        primary,
        "fetch_standings",
        lambda tid: [
            standing_row(1, "clb00036", "Gor Mahia FC", 24),
            standing_row(2, "clb00038", "AFC Leopards", 21),
            standing_row(3, "clb00035", "Tusker FC", 18),
        ],
    )

    result = sync.sync_standings.run()

    assert result["rows"] == 3
    assert result["period"] == "2026-2027"
    assert list(Standing.objects.values_list("position", "points")) == [
        (1, 24),
        (2, 21),
        (3, 18),
    ]


@pytest.mark.django_db
def test_standings_snapshot_invalidates_the_cached_list(monkeypatch, clubs):
    from django.core.cache import cache

    cache.set("standings_list_page_1", {"results": []}, timeout=86400)
    monkeypatch.setattr(
        primary,
        "fetch_standings",
        lambda tid: [standing_row(1, "clb00036", "Gor Mahia FC", 0)],
    )

    sync.sync_standings.run()

    assert cache.get("standings_list_page_1") is None


@pytest.mark.django_db
def test_a_source_outage_leaves_the_existing_table_intact(monkeypatch, clubs):
    """Regression: the old task deleted the table before it fetched anything."""
    Standing.objects.create(
        team=clubs["clb00036"],
        position=1,
        played=10,
        wins=8,
        draws=0,
        losses=2,
        goals_for=20,
        goals_against=5,
        goal_differential=15,
        points=24,
        period="2026-2027",
    )

    def unavailable(_tid):
        raise SourceUnavailable("WAF challenge page")

    monkeypatch.setattr(primary, "fetch_standings", unavailable)

    with pytest.raises(SourceUnavailable):
        sync.sync_standings.run()

    assert Standing.objects.count() == 1, "an outage must not wipe the league table"


@pytest.mark.django_db
def test_an_unknown_club_aborts_instead_of_dropping_rows(monkeypatch, clubs):
    monkeypatch.setattr(
        primary,
        "fetch_standings",
        lambda tid: [
            standing_row(1, "clb00036", "Gor Mahia FC", 24),
            standing_row(2, "clb99999", "Some New Club", 21),
        ],
    )

    with pytest.raises(StructureChanged):
        sync.sync_standings.run()

    assert Standing.objects.count() == 0


@pytest.mark.django_db
def test_an_unpublished_table_is_reported_not_treated_as_an_error(monkeypatch, clubs):
    """Before the first matchday the table is legitimately empty."""
    monkeypatch.setattr(primary, "fetch_standings", lambda tid: [])

    result = sync.sync_standings.run()

    assert result["rows"] == 0
    assert "error" not in result


# --------------------------------------------------------------------------- #
# Gameweeks
# --------------------------------------------------------------------------- #


def fixture_row(day, home, away, home_id, away_id, fixture_id, matchday=None):
    return primary.FixtureRow(
        provider_fixture_id=fixture_id,
        provider_score_id=None,
        matchday=matchday,
        kickoff=datetime(2026, 8, day, 15, 0),
        has_kickoff_time=True,
        home_team=home,
        away_team=away,
        home_provider_id=home_id,
        away_provider_id=away_id,
        venue="Kasarani",
    )


def test_matchdays_are_rebuilt_when_the_source_does_not_label_them():
    """The fixtures page groups by date only; a round is one game per club."""
    rows = [
        fixture_row(29, "A", "B", "1", "2", "10"),
        fixture_row(29, "C", "D", "3", "4", "11"),
        fixture_row(30, "E", "F", "5", "6", "12"),
        fixture_row(31, "B", "A", "2", "1", "13"),
    ]

    assigned = sync._assign_matchdays(rows, club_count=6)

    # Six clubs means three matches per round: the first three fixtures form
    # matchday 1 and the fourth opens matchday 2.
    assert [matchday for matchday, _ in assigned] == [1, 1, 1, 2]


def test_an_explicit_matchday_from_the_results_page_is_kept():
    rows = [fixture_row(29, "A", "B", "1", "2", "10", matchday=7)]

    assigned = sync._assign_matchdays(rows, club_count=18)

    assert assigned[0][0] == 7


@pytest.mark.django_db
def test_a_deadline_that_has_already_passed_is_never_moved(monkeypatch, clubs):
    """Managers have already picked against it; moving it rewrites history."""
    past = timezone.now() - timedelta(days=3)
    gameweek = Gameweek.objects.create(
        number=1,
        start_date=past.date(),
        end_date=past.date(),
        transfer_deadline=past,
    )

    sync._upsert_gameweeks(
        [
            (
                1,
                fixture_row(
                    29, "Gor Mahia FC", "AFC Leopards", "clb00036", "clb00038", "10"
                ),
            )
        ]
    )

    gameweek.refresh_from_db()
    assert gameweek.transfer_deadline == past


@pytest.mark.django_db
def test_a_future_deadline_tracks_the_first_kick_off(monkeypatch, clubs):
    sync._upsert_gameweeks(
        [
            (
                1,
                fixture_row(
                    29, "Gor Mahia FC", "AFC Leopards", "clb00036", "clb00038", "10"
                ),
            )
        ]
    )

    gameweek = Gameweek.objects.get(number=1)
    kickoff = timezone.make_aware(datetime(2026, 8, 29, 15, 0))
    assert gameweek.transfer_deadline == kickoff - sync.DEADLINE_LEAD


# --------------------------------------------------------------------------- #
# Fixtures and results
# --------------------------------------------------------------------------- #


@pytest.mark.django_db
def test_fixtures_are_keyed_on_the_provider_id_so_a_re_run_is_idempotent(
    monkeypatch, clubs
):
    rows = [
        fixture_row(
            29, "Gor Mahia FC", "AFC Leopards", "clb00036", "clb00038", "12614"
        ),
    ]
    monkeypatch.setattr(primary, "fetch_fixtures", lambda tid: rows)

    first = sync.sync_fixtures.run()
    second = sync.sync_fixtures.run()

    assert first["created"] == 1
    assert second["created"] == 0
    assert Fixture.objects.count() == 1
    assert (
        ExternalFixtureMapping.objects.filter(
            provider=primary.PROVIDER, provider_fixture_id="12614"
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_a_completed_fixture_does_not_get_its_kick_off_rewritten(monkeypatch, clubs):
    played = timezone.make_aware(datetime(2026, 8, 29, 15, 0))
    fixture = Fixture.objects.create(
        home_team=clubs["clb00036"],
        away_team=clubs["clb00038"],
        match_date=played,
        venue="Kasarani",
        status="completed",
    )
    ExternalFixtureMapping.objects.create(
        provider=primary.PROVIDER, provider_fixture_id="12614", fixture=fixture
    )

    moved = fixture_row(
        30, "Gor Mahia FC", "AFC Leopards", "clb00036", "clb00038", "12614"
    )
    monkeypatch.setattr(primary, "fetch_fixtures", lambda tid: [moved])

    sync.sync_fixtures.run()

    fixture.refresh_from_db()
    assert fixture.match_date == played


@pytest.mark.django_db
def test_a_result_with_no_scheduled_fixture_is_back_filled(monkeypatch, clubs):
    """Played matches leave the fixtures page, so a mid-season deploy sees none."""
    result = primary.FixtureRow(
        provider_fixture_id=None,
        provider_score_id="4789",
        matchday=1,
        kickoff=datetime(2026, 8, 29, 15, 0),
        has_kickoff_time=False,
        home_team="Gor Mahia FC",
        away_team="AFC Leopards",
        home_provider_id="clb00036",
        away_provider_id="clb00038",
        venue="",
        home_score=2,
        away_score=1,
    )
    monkeypatch.setattr(primary, "fetch_results", lambda tid: [result])

    report = sync.sync_results.run()

    assert report["created"] == 1
    assert report["unmatched"] == 0
    fixture = Fixture.objects.get()
    assert (fixture.home_team_score, fixture.away_team_score) == (2, 1)
    assert fixture.status == "completed"
    assert fixture.gameweek.number == 1


# --------------------------------------------------------------------------- #
# Locking
# --------------------------------------------------------------------------- #


@pytest.mark.django_db
def test_a_second_run_skips_instead_of_stampeding_the_source(monkeypatch, clubs):
    from apps.kpl.scraping.locks import task_lock

    monkeypatch.setattr(primary, "fetch_standings", lambda tid: [])

    with task_lock("apps.kpl.tasks.sync.sync_standings"):
        result = sync.sync_standings.run()

    assert result == {"skipped": "locked", "task": "apps.kpl.tasks.sync.sync_standings"}
