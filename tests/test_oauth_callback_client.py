"""Regression tests for the client-side OAuth callback reload behaviour."""

from pathlib import Path

CALLBACK = (
    Path(__file__).resolve().parents[1]
    / "client"
    / "src"
    / "views"
    / "Auth"
    / "OAuthCallback.vue"
)


def test_authenticated_reload_of_scrubbed_callback_skips_auth_code_validation():
    """A completed sign-in must not fail after its callback URL is refreshed."""
    body = CALLBACK.read_text()

    assert "if (authStore.isAuthenticated && !query.auth_code)" in body
    assert "        redirectToHome();\n        return;\n    }\n\n    try:" in body
