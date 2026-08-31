"""Regression tests for top-scorer task outcome logging."""

from pathlib import Path

SCORERS_TASK = Path(__file__).resolve().parents[1] / "apps" / "kpl" / "tasks" / "scorers.py"


def test_missing_active_gameweek_is_logged_as_a_warning():
    """A handled no-gameweek result must not be reported as a worker error."""
    body = SCORERS_TASK.read_text()

    assert 'logger.warning("No active gameweek found for scraping scorers")' in body
    assert 'logger.error("No active gameweek found for scraping scorers")' not in body
