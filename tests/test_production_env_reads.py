"""Regression test: production must read env through base.env(), not os.getenv.

``config/settings/production.py`` used to read every database, email, and
Celery variable with raw ``os.getenv()``. base.py defines ``env()`` precisely
because docker-compose's env_file keeps values verbatim: a trailing space on a
line in .env.prod reaches the process intact. A space inside a password,
broker URL, or link domain fails far from the cause — Postgres auth errors on
every request, kombu cannot parse the broker URL so CeleryEmailBackend queues
mail that never sends, and DOMAIN poisons activation links.

The other half is quieter still. An unset variable became None and Django
booted cleanly, failing later on the first query or first queued email —
possibly only under load.
"""

import pytest
from django.core.exceptions import ImproperlyConfigured

import config.settings.production as production


def test_every_env_read_goes_through_the_whitespace_guard():
    """os.getenv in this module is exactly the bug: it skips base.env()."""
    import inspect

    source = inspect.getsource(production)
    assert "os.getenv(" not in source


def test_reads_are_whitespace_tolerant(monkeypatch):
    """A trailing space must be stripped before it becomes a credential."""
    monkeypatch.setenv("PG_PASSWORD", "hunter2 ")
    assert production.env("PG_PASSWORD") == "hunter2"


def test_a_missing_required_variable_stops_startup():
    """None must never reach DATABASES or CELERY_BROKER_URL silently."""
    for name in production._REQUIRED_ENV:
        assert production.env(name), (
            f"{name} is unset or blank; production.py should have raised "
            "ImproperlyConfigured at import"
        )


def test_the_guard_actually_raises_when_something_is_missing(monkeypatch):
    """The check is only worth having if it fires."""
    monkeypatch.delenv("PG_HOST", raising=False)
    with pytest.raises(ImproperlyConfigured):
        production.require_env(production._REQUIRED_ENV)


def test_email_port_is_an_integer():
    """smtplib tolerates a string port; anything that formats one won't."""
    assert isinstance(production.EMAIL_PORT, int)
