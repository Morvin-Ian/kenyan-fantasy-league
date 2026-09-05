"""Lineup adapter for the primary source.

The earlier version drove this page through Selenium. It never needed to: the
match report is static server-rendered HTML with a plain three-column lineup
table, so it is fetched over HTTP through
:mod:`apps.kpl.scraping.providers.primary` and the browser is skipped entirely.
That removes a Chrome session, its memory, and its failure modes from the
lineup path.

Only published (post-match) lineups exist on this source: it is a settlement
source, not a pre-match team-news one.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

from apps.kpl.scraping import ScrapeError
from apps.kpl.scraping.providers import primary

logger = logging.getLogger(__name__)

_MATCH_ID = re.compile(r"(\d+)\s*$")

NEEDS_BROWSER = False


def extract_match_id(url: str) -> Optional[str]:
    match = _MATCH_ID.search((url or "").strip())
    return match.group(1) if match else None


def scrape_lineups(url: str) -> Dict[str, Dict[str, Any]]:
    """Return ``{"home": {...}, "away": {...}}`` for a match report URL."""
    match_id = extract_match_id(url)
    if not match_id:
        logger.warning("cannot read a match-report id out of %r", url)
        return {}

    try:
        detail = primary.fetch_match_detail(match_id)
    except ScrapeError as exc:
        logger.warning("lineup fetch failed for match report %s: %s", match_id, exc)
        return {}

    def side(starters, bench) -> Dict[str, Any]:
        return {
            "formation": None,
            # The report is published after the match, so the XI is final.
            "is_confirmed": True,
            "published_at": detail.kickoff,
            "starters": [{"name": name} for name in starters],
            "bench": [{"name": name} for name in bench],
        }

    return {
        "home": side(detail.home_starters, detail.home_bench),
        "away": side(detail.away_starters, detail.away_bench),
    }
