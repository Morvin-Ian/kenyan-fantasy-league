"""Regression coverage for the fixture scraper's required source URL."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_EXAMPLE = REPO_ROOT / ".env.example"
SETTINGS = REPO_ROOT / "config" / "settings" / "base.py"
FIXTURES_TASK = REPO_ROOT / "apps" / "kpl" / "tasks" / "fixtures.py"


def test_fixture_source_url_is_documented_for_worker_environment_files():
    """Operators must be able to configure the scheduled worker's source URL."""
    assert "TEAM_FIXTURES_URL=" in ENV_EXAMPLE.read_text()


def test_fixture_task_uses_the_hardened_documented_setting():
    """The scraper must consume the same setting that the environment documents."""
    assert 'TEAM_FIXTURES_URL = env("TEAM_FIXTURES_URL")' in SETTINGS.read_text()
    assert "url = base.TEAM_FIXTURES_URL" in FIXTURES_TASK.read_text()
