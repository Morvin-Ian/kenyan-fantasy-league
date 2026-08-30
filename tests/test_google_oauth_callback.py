"""Regression tests for Google OAuth callback outcome logging."""

from pathlib import Path

VIEWS = Path(__file__).resolve().parents[1] / "apps" / "accounts" / "views.py"


def test_missing_google_authorization_code_is_logged_as_a_warning():
    """An expected cancelled or incomplete callback must not emit an error."""
    body = VIEWS.read_text()

    assert 'logger.warning("No authorization code received from Google")' in body
    assert 'logger.error("No authorization code received from Google")' not in body
