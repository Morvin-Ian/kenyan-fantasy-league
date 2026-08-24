"""Regression test: the fixtures scraper validates its inputs and logs failures
in a way that can be acted on.

``extract_fixtures_data`` reads ``TEAM_FIXTURES_URL`` from the environment and
parses a SportPress ``table.sp-event-blocks`` out of the fetched page. Two
failure modes were silent or indistinguishable:

- ``TEAM_FIXTURES_URL`` unset: ``requests.get(None)`` raised ``MissingSchema``,
  which the ``except requests.RequestException`` swallowed into a confusing
  "Error fetching fixtures" line. The sibling scrapers (standings.py:21-24,
  players.py:77-79) all guard ``if not url`` first.
- The page returned 200 without the expected table (markup drift, a bot wall,
  an off-season "no fixtures" page): only a bare "No fixtures table found"
  line was logged, discarding the very content that would say which.
"""

import logging

import requests

from apps.kpl.tasks.fixtures import extract_fixtures_data
from util.views import headers


class _FakeResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


def test_unset_url_is_reported_without_a_request(monkeypatch, caplog):
    """An unset TEAM_FIXTURES_URL must fail fast, not hit the network."""
    monkeypatch.delenv("TEAM_FIXTURES_URL", raising=False)

    def _fail(*args, **kwargs):
        raise AssertionError("requests.get must not be called without a URL")

    monkeypatch.setattr(requests, "get", _fail)

    with caplog.at_level(logging.ERROR, logger="apps.kpl.tasks.fixtures"):
        assert extract_fixtures_data(headers) is False

    assert "TEAM_FIXTURES_URL environment variable not set" in caplog.text


def test_missing_table_logs_html_preview(monkeypatch, caplog):
    """A 200 page without the table must keep the HTML that explains why."""
    monkeypatch.setenv("TEAM_FIXTURES_URL", "https://example.test/fixtures")

    page = "<html><body><h1>Fixtures</h1><p>No scheduled matches</p></body></html>"
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(status_code=200, text=page),
    )

    with caplog.at_level(logging.ERROR, logger="apps.kpl.tasks.fixtures"):
        assert extract_fixtures_data(headers) is False

    assert "No fixtures table found on the page." in caplog.text
    assert page[:1000] in caplog.text
