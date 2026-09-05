"""Regression tests for Google OAuth callback outcome logging."""

from pathlib import Path

VIEWS = Path(__file__).resolve().parents[1] / "apps" / "accounts" / "views.py"


def test_missing_google_authorization_code_is_logged_as_a_warning():
    """An expected cancelled or incomplete callback must not emit an error."""
    body = VIEWS.read_text()

    assert 'logger.warning("No authorization code received from Google")' in body
    assert 'logger.error("No authorization code received from Google")' not in body


def test_callback_only_uses_a_signed_oauth_state_for_its_redirect_target():
    """A query-string state must not be able to choose the callback redirect."""
    body = VIEWS.read_text()

    assert "redirect_to = settings.FRONTEND_URL" in body
    assert 'request.GET.get("redirect_to", settings.FRONTEND_URL)' not in body
    assert "state = signing.dumps(state_data)" in body
    assert "state_data = signing.loads(state)" in body
    assert "except signing.BadSignature as e:" in body
    assert "auth_message=invalid_state" in body
