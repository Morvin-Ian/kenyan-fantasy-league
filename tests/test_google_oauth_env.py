"""Regression test: Google OAuth credentials must come from the hardened
settings, never from a raw ``os.getenv``.

docker-compose's ``env_file:`` passes values verbatim, so a trailing space or
newline artifact on ``GOOGLE_CLIENT_ID`` / ``GOOGLE_CLIENT_SECRET`` in
``.env`` / ``.env.prod`` reaches the process environment intact.
``config/settings/base.env()`` strips that whitespace; the Google OAuth service
in ``apps/accounts/services.py`` used to bypass the settings module and re-read
the raw environment, so the corrupted value was sent to Google's token
endpoint *and* compared against in the ID-token audience check, breaking every
"Continue with Google" sign-in with ``Failed to exchange authorization code``
or ``Token audience mismatch`` (incident ``b63a7039aeb50622``).

These tests fail on the pre-fix code (``os.getenv("GOOGLE_CLIENT_ID")`` in
``services.py``) and pass on the hardened code, which reads
``base.GOOGLE_CLIENT_ID`` / ``base.GOOGLE_CLIENT_SECRET``.
"""

from pathlib import Path

import pytest

from config.settings.base import env

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICES = REPO_ROOT / "apps" / "accounts" / "services.py"
SETTINGS = REPO_ROOT / "config" / "settings" / "base.py"


def test_services_imports_the_hardened_settings_module():
    """The single source of truth is config.settings.base, not the process env."""
    body = SERVICES.read_text()
    assert "from config.settings import base" in body


def test_token_exchange_sends_the_trimmed_client_id_and_secret():
    """The POST to oauth2.googleapis.com/token must use base's values."""
    body = SERVICES.read_text()
    assert '"client_id": base.GOOGLE_CLIENT_ID' in body
    assert '"client_secret": base.GOOGLE_CLIENT_SECRET' in body


def test_audience_check_uses_the_trimmed_client_id():
    """The ID-token aud comparison must use the same hardened value."""
    body = SERVICES.read_text()
    assert 'token_info.get("aud") != base.GOOGLE_CLIENT_ID' in body


def test_no_raw_os_getenv_reads_of_google_credentials_remain():
    """Any regression back to os.getenv re-opens the whitespace corruption."""
    body = SERVICES.read_text()
    assert 'os.getenv("GOOGLE_CLIENT_ID")' not in body
    assert 'os.getenv("GOOGLE_CLIENT_SECRET")' not in body


def test_settings_define_the_credentials_through_the_trimming_helper():
    """The settings half of the contract: env(), never bare os.getenv."""
    body = SETTINGS.read_text()
    assert 'GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")' in body
    assert 'GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")' in body
    assert 'os.getenv("GOOGLE_CLIENT_ID")' not in body
    assert 'os.getenv("GOOGLE_CLIENT_SECRET")' not in body


def test_env_helper_strips_stray_whitespace(monkeypatch):
    """The property the whole incident turns on: env() trims, os.getenv does not."""
    monkeypatch.setenv(
        "GOOGLE_CLIENT_ID", " 1234-abcd.apps.googleusercontent.com "
    )
    assert env("GOOGLE_CLIENT_ID") == "1234-abcd.apps.googleusercontent.com"


def test_env_helper_leaves_non_string_values_alone(monkeypatch):
    """A non-str value must pass through unchanged, not crash .strip()."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "anything")
    assert env("GOOGLE_CLIENT_ID", default=None) is not None
    assert env("NEVER_SET_VAR_92D7C9DF", default=None) is None
