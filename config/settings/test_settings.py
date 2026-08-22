"""Regression tests for ALLOWED_HOSTS.

Incident: Django rejected every request with Host: fantasykenya.com
(DisallowedHost) because ALLOWED_HOSTS came only from the deployment's
ALLOWED_HOSTS env var, whose value excludes the site's real domains.
"""

import importlib

import config.settings.base as base_settings


def test_production_domains_allowed_even_when_env_has_stale_value(monkeypatch):
    """A stale ALLOWED_HOSTS env var (e.g. a dev value like "localhost api")
    must not be able to reject the site's own domains."""
    monkeypatch.setenv("ALLOWED_HOSTS", "localhost api")
    importlib.reload(base_settings)
    assert "fantasykenya.com" in base_settings.ALLOWED_HOSTS
    assert "www.fantasykenya.com" in base_settings.ALLOWED_HOSTS


def test_production_domains_allowed_when_env_unset(monkeypatch):
    """With no ALLOWED_HOSTS env var the wildcard default applies, and the
    production domains are accepted either way."""
    monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
    importlib.reload(base_settings)
    assert "*" in base_settings.ALLOWED_HOSTS
    assert "fantasykenya.com" in base_settings.ALLOWED_HOSTS
    assert "www.fantasykenya.com" in base_settings.ALLOWED_HOSTS
