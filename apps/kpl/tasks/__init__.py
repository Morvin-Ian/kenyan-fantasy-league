"""Celery task registry for the kpl app.

``autodiscover_tasks`` imports ``<app>.tasks`` and nothing deeper, so a task
module missing from this list is never registered and its schedule entries fail
with ``NotRegistered``. Every task module belongs here.
"""

from . import gameweeks, live_games, sync  # noqa: F401
from .fixtures import update_active_gameweek
from .lineups import fetch_lineup_for_fixture_task, scan_upcoming_fixtures_for_lineups
from .sync import (
    sync_all,
    sync_fixtures,
    sync_match_details,
    sync_players,
    sync_results,
    sync_standings,
    sync_team_logos,
    sync_teams,
    sync_top_scorers,
)

__all__ = [
    "sync_all",
    "sync_teams",
    "sync_team_logos",
    "sync_fixtures",
    "sync_results",
    "sync_players",
    "sync_standings",
    "sync_top_scorers",
    "sync_match_details",
    "update_active_gameweek",
    "scan_upcoming_fixtures_for_lineups",
    "fetch_lineup_for_fixture_task",
]
