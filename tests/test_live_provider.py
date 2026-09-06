"""Parser coverage for the live-score provider.

Runs against a saved copy of the real rendered DOM in
``tests/fixtures/source_live``, with the source's name and asset host scrubbed.
The page is drawn entirely by JavaScript, so this fixture is the browser's
output rather than the served HTML — a redesign shows up as a failure here
instead of as fixtures that silently stop updating.
"""

from datetime import date
from pathlib import Path

import pytest
from django.test import override_settings

from apps.kpl.scraping.exceptions import StructureChanged
from apps.kpl.scraping.providers import live

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "source_live"
TODAY = date(2026, 9, 6)

LIVE_SETTINGS = {
    "SCRAPER_LIVE_BASE_URL": "https://source.invalid/",
    "SCRAPER_LIVE_PATH": "scores/football",
    "SCRAPER_LIVE_COMPETITION": "Example League",
}


@pytest.fixture
def page() -> str:
    return (FIXTURES / "scores.html").read_text(encoding="utf-8")


def test_every_match_row_is_read(page):
    matches = live.parse_scores(page, today=TODAY)

    assert len(matches) > 100
    assert all(m.home_team and m.away_team for m in matches)
    assert all(m.home_team != m.away_team for m in matches)


def test_a_played_match_carries_both_scores(page):
    matches = live.parse_scores(page, today=TODAY)
    played = [m for m in matches if m.is_played]

    assert played
    sample = next(m for m in played if m.home_team == "Kariobangi Sharks")
    assert (sample.home_score, sample.away_score) == (7, 1)
    assert sample.away_team == "Sofapaka"
    assert sample.status == "completed"


def test_the_club_name_comes_from_the_logo_not_the_truncated_label(page):
    """The sibling text is clipped for width on narrow columns."""
    matches = live.parse_scores(page, today=TODAY)
    names = {m.home_team for m in matches} | {m.away_team for m in matches}

    assert "Gor Mahia" in names
    assert "Kakamega Homeboyz" in names
    assert not any(name.endswith("...") for name in names)


def test_a_date_without_a_year_is_read_into_the_right_one(page):
    """The source omits the year, and a season page spans about ten months.

    The state decides it: a match that has ended cannot be in the future. Any
    fixed day-window heuristic mis-reads one end of the season — a 200-day one
    pushed 177 of last season's results a year forward.
    """
    matches = live.parse_scores(page, today=TODAY)
    finished = [m for m in matches if m.match_date and m.status == "completed"]

    assert finished
    assert all(m.match_date <= TODAY for m in finished)
    # And they land in the season just gone, not years adrift.
    assert all((TODAY - m.match_date).days < 400 for m in finished)


def test_an_unplayed_fixture_is_read_as_the_next_time_it_comes_round(page):
    matches = live.parse_scores(page, today=TODAY)
    upcoming = [m for m in matches if m.match_date and m.status == "upcoming"]

    assert all(m.match_date >= TODAY for m in upcoming)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("ended", "completed"),
        ("FT", "completed"),
        ("firsthalf", "live"),
        ("secondhalf", "live"),
        ("halftime", "live"),
        ("notstarted", "upcoming"),
        ("postponed", "postponed"),
        ("cancelled", "postponed"),
        ("67'", "live"),
        # A row that shows the kick-off time has not started.
        ("13:00", "upcoming"),
        ("3:30 PM", "upcoming"),
    ],
)
def test_match_states_map_onto_fixture_status(raw, expected):
    assert live._status_for(raw) == expected


def test_an_unrecognised_state_is_not_treated_as_finished():
    """Settling a match that is still being played would award points early."""
    assert live._status_for("something new") == "upcoming"
    assert live._status_for("") == "upcoming"


def test_a_page_that_rendered_nothing_is_reported_not_silently_empty():
    """An empty parse would look exactly like a quiet afternoon."""
    with pytest.raises(StructureChanged):
        live.parse_scores("<html><body><div>no matches</div></body></html>")


def test_the_source_is_not_named_in_the_code():
    """Every host lives in the environment, as with the primary provider."""
    source = Path(live.__file__).read_text(encoding="utf-8")
    assert "tisini" not in source.lower()

    with override_settings(**LIVE_SETTINGS):
        assert live.scores_url() == "https://source.invalid/scores/football"
        assert live.competition() == "Example League"


def test_missing_configuration_is_reported_clearly():
    with override_settings(SCRAPER_LIVE_BASE_URL="", SCRAPER_LIVE_PATH=""):
        with pytest.raises(live.LiveSourceNotConfigured):
            live.scores_url()
