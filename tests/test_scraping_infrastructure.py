"""Regression coverage for the scraping layer's stability guarantees.

These lock down the defects that stopped the workers producing any data at all:

* ``apps/kpl/scrapers`` was deleted while ``apps/kpl/tasks/lineups.py`` still
  imported it, so that module raised ImportError and every lineup task was
  missing from the worker's registry.
* ``apps/kpl/services.py`` was shadowed by the ``apps/kpl/services/`` package,
  so ``from apps.kpl.services import upsert_fixture_lineup`` could never resolve.
* ``apps/kpl/tasks/__init__.py`` imported only three of the task modules.
  ``autodiscover_tasks`` imports ``<app>.tasks`` and nothing deeper, so the
  lineup tasks were never registered even though they existed.
* Team names differ between sources ("Mathare UTD" vs "Mathare United"), which
  silently created duplicate clubs.
"""

import importlib
import re
from pathlib import Path
from urllib.parse import urlparse

import pytest
from django.test import override_settings

REPO_ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------- #
# Import paths that used to be broken
# --------------------------------------------------------------------------- #


def test_lineup_scrapers_package_exists():
    """apps.kpl.tasks.lineups imports this; without it the module cannot load."""
    module = importlib.import_module("apps.kpl.scrapers")

    assert callable(module.detect_provider_from_url)
    assert callable(module.scrape_lineups_for_url)
    with override_settings(SCRAPER_PROVIDER_HOSTS="primary=source.invalid"):
        assert (
            module.detect_provider_from_url("https://source.invalid/match.php?s=1")
            == "primary"
        )
        assert module.detect_provider_from_url("https://elsewhere.invalid/x") is None


def test_services_package_re_exports_the_shadowed_module():
    from apps.kpl.services import upsert_fixture_lineup

    assert callable(upsert_fixture_lineup)


def test_services_package_does_not_close_a_circular_import():
    """LineupService/PlayerService reach back into apps.kpl.tasks."""
    services = importlib.import_module("apps.kpl.services")

    assert services.LineupService is not None
    assert services.PlayerService is not None


def test_every_task_module_is_imported_by_the_registry():
    """A task module missing from tasks/__init__.py is invisible to Celery."""
    registry = (REPO_ROOT / "apps" / "kpl" / "tasks" / "__init__.py").read_text()
    modules = {
        path.stem
        for path in (REPO_ROOT / "apps" / "kpl" / "tasks").glob("*.py")
        if path.stem not in {"__init__", "base"}
    }

    missing = {name for name in modules if name not in registry}
    assert not missing, f"task modules not imported in tasks/__init__.py: {sorted(missing)}"


def test_scraping_tasks_are_registered_with_celery():
    import apps.kpl.tasks  # noqa: F401  (registers the tasks)
    from config.celery import app

    expected = {
        "apps.kpl.tasks.sync.sync_teams",
        "apps.kpl.tasks.sync.sync_fixtures",
        "apps.kpl.tasks.sync.sync_results",
        "apps.kpl.tasks.sync.sync_players",
        "apps.kpl.tasks.sync.sync_standings",
        "apps.kpl.tasks.sync.sync_top_scorers",
        "apps.kpl.tasks.sync.sync_match_details",
        "apps.kpl.tasks.lineups.scan_upcoming_fixtures_for_lineups",
    }
    assert expected <= set(app.tasks)


def test_every_scheduled_task_exists():
    """A beat entry naming a task no worker knows about fails as NotRegistered."""
    import apps.kpl.tasks  # noqa: F401
    from django.conf import settings

    from config.celery import app

    for entry, config in settings.CELERY_BEAT_SCHEDULE.items():
        assert config["task"] in app.tasks, f"beat entry '{entry}' names an unknown task"


# --------------------------------------------------------------------------- #
# Name normalisation
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "left,right",
    [
        ("Mathare UTD", "Mathare United"),
        ("Muranga SEAL", "Murang'a Seal FC"),
        ("Gor Mahia FC", "Gor Mahia"),
        ("Kenya Police FC", "Kenya Police"),
        ("Ulinzi Stars FC", "Ulinzi Stars"),
        ("Bandari FC", "Bandari Mtwara"),
        ("APS Bomet FC", "APS Bomet"),
        ("AFC Leopards", "AFC Leopards FC"),
        ("KCB FC", "KCB"),
    ],
)
def test_the_same_club_matches_across_sources(left, right):
    from apps.kpl.scraping.normalize import teams_match

    assert teams_match(left, right), f"{left!r} should match {right!r}"


@pytest.mark.parametrize(
    "left,right",
    [
        ("Nairobi United", "Mombasa United"),
        ("Gor Mahia", "Mara Sugar"),
        ("Posta Rangers", "Migori Youth"),
    ],
)
def test_different_clubs_do_not_collide(left, right):
    from apps.kpl.scraping.normalize import teams_match

    assert not teams_match(left, right)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Joe Joseph IRUNGU WAITHIRA", "Joe Joseph Irungu Waithira"),
        ("Elvis Noor  54'", "Elvis Noor"),
        ("  Victor OMONDI OTIENO 91' ", "Victor Omondi Otieno"),
    ],
)
def test_player_names_are_normalised(raw, expected):
    from apps.kpl.scraping.normalize import clean_player_name

    assert clean_player_name(raw) == expected


@pytest.mark.parametrize("raw", ["45'", ",,,,,,, ............", "", "   ", "-"])
def test_non_names_are_rejected(raw):
    from apps.kpl.scraping.normalize import clean_player_name

    assert clean_player_name(raw) is None


# --------------------------------------------------------------------------- #
# HTTP hardening
# --------------------------------------------------------------------------- #


def test_every_scrape_sets_a_timeout():
    """A socket with no timeout wedges the worker slot it runs in."""
    body = (REPO_ROOT / "apps" / "kpl" / "scraping" / "http.py").read_text()

    assert "DEFAULT_TIMEOUT = (10, 45)" in body
    assert "timeout=timeout" in body


def test_a_parked_or_error_page_is_not_treated_as_data(monkeypatch):
    """A dead source can answer 200 with a small empty shell; that is not data."""
    from apps.kpl.scraping import http
    from apps.kpl.scraping.exceptions import SourceUnavailable

    class Stub:
        status_code = 200
        encoding = "utf-8"
        headers = {"Content-Type": "text/html"}
        text = "<html><body>nothing here</body></html>"

    monkeypatch.setattr(http, "get_session", lambda: type("S", (), {"get": lambda *a, **k: Stub()})())
    monkeypatch.setattr(http, "_throttle", lambda *a, **k: None)

    with pytest.raises(SourceUnavailable):
        http.fetch("https://example.test/page")


def test_transient_network_failure_becomes_a_retryable_error(monkeypatch):
    import requests

    from apps.kpl.scraping import http
    from apps.kpl.scraping.exceptions import SourceUnavailable

    def boom(*args, **kwargs):
        raise requests.ConnectionError("connection reset")

    monkeypatch.setattr(http, "get_session", lambda: type("S", (), {"get": staticmethod(boom)})())
    monkeypatch.setattr(http, "_throttle", lambda *a, **k: None)

    with pytest.raises(SourceUnavailable):
        http.fetch("https://example.test/page")


def test_scraping_tasks_retry_only_transient_failures():
    """Retrying a ParseError just re-downloads the same broken page."""
    from apps.kpl.scraping.exceptions import ParseError, SourceUnavailable
    from apps.kpl.tasks.base import ScrapingTask

    assert SourceUnavailable in ScrapingTask.autoretry_for
    assert ParseError not in ScrapingTask.autoretry_for
    assert ScrapingTask.acks_late is True
    assert ScrapingTask.time_limit > ScrapingTask.soft_time_limit


def test_no_source_hostname_is_committed_to_the_repository():
    """Every upstream host lives in the gitignored .env, never in the source tree.

    The banned list is derived from the configured environment rather than
    written out here, so this test names no source either — and it keeps working
    if a source is swapped.
    """
    from django.conf import settings

    configured = " ".join(
        str(getattr(settings, name, ""))
        for name in (
            "SCRAPER_PRIMARY_BASE_URL",
            "SCRAPER_PROVIDER_HOSTS",
        )
    )
    hosts = {
        # Registrable part only: "sub.example.co.uk" -> "example".
        part.split(".")[-2] if len(part.split(".")) > 1 else part
        for chunk in re.split(r"[\s,=]+", configured)
        for part in [urlparse(chunk if "//" in chunk else f"//{chunk}").netloc]
        if part and "." in part
    }
    hosts = {h for h in hosts if len(h) > 4 and h not in {"local", "invalid"}}

    if not hosts:
        pytest.skip("no scraping sources configured in this environment")

    offenders = []
    for path in (REPO_ROOT / "apps").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        lowered = path.read_text().lower()
        offenders += [f"{path.relative_to(REPO_ROOT)}: {h}" for h in hosts if h in lowered]

    assert not offenders, "source hostnames must live in .env only: " + ", ".join(offenders)


def test_provider_refuses_to_run_unconfigured():
    """A missing SCRAPER_* setting must say so, not silently scrape nothing."""
    from apps.kpl.scraping.providers import primary

    with override_settings(SCRAPER_PRIMARY_BASE_URL=""):
        with pytest.raises(primary.SourceNotConfigured):
            primary.base_url()

    with override_settings(
        SCRAPER_PRIMARY_BASE_URL="https://source.invalid/", SCRAPER_PRIMARY_PATHS=""
    ):
        with pytest.raises(primary.SourceNotConfigured):
            primary.path_for("standings", season="x")
