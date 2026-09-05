"""Parser coverage for the primary provider.

Every test runs against a saved copy of a real page in
``tests/fixtures/source_primary``, with the source's hostname scrubbed out. The
suite never touches the network, so a source redesign shows up as a failing
assertion here rather than as an empty league table in production.

Background — the three failures these lock down:

* the standings URL pointed at a site whose HTML is served behind a WAF
  challenge, so the scraper parsed a JavaScript challenge page and found no
  table at all;
* the fixtures URL pointed at a site that had stopped rendering the table the
  parser looked for, and now returns an empty JavaScript shell;
* the scorers task hard-coded one season's competition id, so it kept
  re-reading a finished competition after the season rolled over.
"""

from datetime import date
from pathlib import Path

import pytest
from django.test import override_settings

from apps.kpl.scraping.exceptions import StructureChanged
from apps.kpl.scraping.providers import primary

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "source_primary"

# Stand-ins for the real values, which live only in .env / .env.prod. The saved
# pages have had the real host and id prefixes replaced to match.
SOURCE_BASE = "https://source.invalid/"
COMPETITION = "Kenya Premier League"
CURRENT_SEASON = "cmp0122"
PAST_SEASON = "cmp0043"

SOURCE_SETTINGS = {
    "SCRAPER_PRIMARY_BASE_URL": SOURCE_BASE,
    "SCRAPER_PRIMARY_COMPETITION": COMPETITION,
    "SCRAPER_PRIMARY_PATHS": ",".join(
        [
            "index=index.php",
            "teams=teams.php?t={season}",
            "standings=standings.php?t={season}",
            "fixtures=fixtures.php?t={season}",
            "results=results.php?t={season}",
            "scorers=scorers.php?t={season}",
            "squads=squads.php?t={season}",
            "match=match.php?s={match}",
        ]
    ),
}

pytestmark = pytest.mark.usefixtures("source_settings")


@pytest.fixture
def source_settings():
    """Point the provider at placeholder config for the whole module."""
    with override_settings(**SOURCE_SETTINGS):
        yield


def page(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.fixture
def served(monkeypatch):
    """Serve a saved page for whatever URL the provider asks for."""

    def _serve(name: str):
        from apps.kpl.scraping import http

        def fake_fetch(url, **kwargs):
            return http.Response(url=url, status_code=200, text=page(name))

        monkeypatch.setattr(primary, "fetch", fake_fetch)

    return _serve


# --------------------------------------------------------------------------- #
# Season discovery
# --------------------------------------------------------------------------- #


def test_season_is_discovered_not_hard_coded(served):
    """The newest KPL season wins, so a rollover needs no code change."""
    served("index.html")
    season = primary.discover_current_season()

    assert season.tournament_id == CURRENT_SEASON
    assert season.start_year == 2026
    assert season.end_year == 2027


def test_season_discovery_ignores_other_competitions(served):
    """A women's competition shares most of the label and must not win."""
    served("index.html")
    season = primary.discover_current_season()

    assert "Women" not in season.label
    assert season.label.startswith(COMPETITION)


def test_no_season_raises_rather_than_returning_a_stale_default(monkeypatch):
    from apps.kpl.scraping import http
    from apps.kpl.scraping.exceptions import SeasonNotFound

    monkeypatch.setattr(
        primary,
        "fetch",
        lambda url, **kw: http.Response(url=url, status_code=200, text="<html></html>"),
    )
    with pytest.raises(SeasonNotFound):
        primary.discover_current_season()


# --------------------------------------------------------------------------- #
# League table
# --------------------------------------------------------------------------- #


def test_standings_parse_every_club_with_its_record(served):
    served("standings.html")
    rows = primary.fetch_standings(PAST_SEASON)

    assert len(rows) == 18
    leader = rows[0]
    assert leader.position == 1
    assert leader.team_name == "Gor Mahia FC"
    assert (leader.played, leader.wins, leader.draws, leader.losses) == (34, 20, 9, 5)
    assert (leader.goals_for, leader.goals_against) == (50, 22)
    assert leader.goal_differential == 28  # source writes "+28"
    assert leader.points == 69
    assert leader.provider_team_id == "clb00036"
    assert leader.logo_url.startswith(SOURCE_BASE)


def test_standings_reject_a_table_whose_columns_moved(monkeypatch):
    """A layout change must fail loudly instead of writing partial rows."""
    from apps.kpl.scraping import http

    monkeypatch.setattr(
        primary,
        "fetch",
        lambda url, **kw: http.Response(
            url=url,
            status_code=200,
            text="<table><tr><th>#</th><th>Team</th><th>P</th></tr></table>",
        ),
    )
    with pytest.raises(StructureChanged):
        primary.fetch_standings(CURRENT_SEASON)


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


def test_fixtures_carry_date_time_venue_and_a_stable_id(served):
    served("fixtures.html")
    fixtures = primary.fetch_fixtures(CURRENT_SEASON)

    assert fixtures, "no fixtures parsed"
    opener = next(
        f
        for f in fixtures
        if f.home_team == "Gor Mahia FC" and f.away_team == "Muranga SEAL"
    )
    assert opener.kickoff.date() == date(2026, 8, 29)
    assert opener.kickoff.hour == 15
    assert opener.venue == "Kasarani International Stadium"
    assert opener.provider_fixture_id == "12614"
    assert opener.home_provider_id == "clb00036"
    assert not opener.is_played


def test_fixture_venue_is_never_the_away_clubs_name(served):
    """Regression: a positional cell fallback used to store the away club as the venue."""
    served("fixtures.html")
    fixtures = primary.fetch_fixtures(CURRENT_SEASON)

    for fixture in fixtures:
        assert fixture.venue != fixture.away_team
        assert fixture.venue != fixture.home_team


def test_derby_marker_is_stripped_from_the_venue(served):
    served("fixtures.html")
    fixtures = primary.fetch_fixtures(CURRENT_SEASON)

    assert not any(f.venue.startswith("Derby") for f in fixtures)


# --------------------------------------------------------------------------- #
# Results
# --------------------------------------------------------------------------- #


def test_results_carry_the_score_and_the_matchday(served):
    served("results.html")
    results = primary.fetch_results(PAST_SEASON)

    assert results
    for row in results:
        assert row.is_played
        assert row.provider_score_id
    assert any(row.matchday for row in results)


def test_results_are_deduplicated_by_provider_id(served):
    """The source repeats recent results in trailing date-only tables."""
    served("results.html")
    results = primary.fetch_results(PAST_SEASON)

    ids = [row.provider_score_id for row in results]
    assert len(ids) == len(set(ids))


# --------------------------------------------------------------------------- #
# Scorers
# --------------------------------------------------------------------------- #


def test_scorers_are_ranked_by_goals_and_keep_their_provider_id(served):
    served("scorers.html")
    scorers = primary.fetch_scorers(PAST_SEASON, limit=5)

    assert len(scorers) == 5
    assert scorers[0].player_name == "Joe Joseph Irungu Waithira"
    assert scorers[0].goals == 19
    assert scorers[0].provider_player_id == "plr0000955"
    assert scorers[0].team_name == "Muranga SEAL"
    assert [s.goals for s in scorers] == sorted(
        (s.goals for s in scorers), reverse=True
    )


# --------------------------------------------------------------------------- #
# Squads
# --------------------------------------------------------------------------- #


def test_squads_pair_each_club_with_its_registered_players(served):
    served("squads.html")
    squads = primary.fetch_squads(CURRENT_SEASON)

    assert squads
    squad = squads[0]
    assert squad.provider_team_id
    assert squad.team_name and "Squad" not in squad.team_name
    assert squad.players
    assert all(p.provider_player_id for p in squad.players)


def test_placeholder_squad_rows_are_dropped(served):
    """One club registers a row literally named ',,,,,,, ............'."""
    served("squads.html")
    squads = primary.fetch_squads(CURRENT_SEASON)

    for squad in squads:
        for player in squad.players:
            assert any(ch.isalpha() for ch in player.name)


# --------------------------------------------------------------------------- #
# Match report
# --------------------------------------------------------------------------- #


def test_match_report_yields_score_goals_cards_and_both_lineups(served):
    served("match_report.html")
    detail = primary.fetch_match_detail("8387")

    assert (detail.home_team, detail.away_team) == ("Shabana FC", "KCB FC")
    assert (detail.home_score, detail.away_score) == (1, 2)
    assert detail.venue == "Green Stadium Awendo"

    assert len(detail.goals) == 3
    late = next(g for g in detail.goals if g.minute == 91)
    assert late.player_name == "Victor Omondi Otieno"
    assert late.team_side == "home"

    assert len(detail.cards) == 1
    card = detail.cards[0]
    assert (card.card, card.minute, card.team_name) == ("yellow", 50, "KCB FC")
    assert card.player_name == "David Sakwa Nyongesa"

    assert len(detail.home_starters) == 11
    assert len(detail.away_starters) == 11
    assert detail.home_bench and detail.away_bench


def test_match_report_rejects_a_page_that_is_not_a_result(monkeypatch):
    from apps.kpl.scraping import http

    monkeypatch.setattr(
        primary,
        "fetch",
        lambda url, **kw: http.Response(
            url=url, status_code=200, text="<html><title>Not a match</title></html>"
        ),
    )
    with pytest.raises(StructureChanged):
        primary.fetch_match_detail("1")
