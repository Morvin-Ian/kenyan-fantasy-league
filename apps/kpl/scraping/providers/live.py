"""Live-score provider.

Unlike the primary source, this one renders entirely in the browser: the served
HTML is an empty shell and every match is drawn by JavaScript. There is no
server-rendered markup to read, so this adapter drives a real browser, applies
the site's own competition filter, and parses the DOM that results — the same
thing a visitor's browser does. Nothing here reads or stores any credential.

As with every other provider, nothing in this module names the source. The base
URL, the page path and the competition label all come from ``SCRAPER_LIVE_*``
in the environment.

What the rendered rows carry, per match::

    <div class="grid grid-cols-12 ...">
      <div class="col-span-2">  date, then status ("ended", "firsthalf", ...)
      <div class="col-span-3">  home club: name, then a logo whose alt is the name
      <div class="col-span-2">  "1 - 2", or the kick-off time if not played
      <div class="col-span-4">  away club: logo, then name

The club names are read from the logos' ``alt`` attributes, which carry the
club name on its own; the sibling text nodes are sometimes truncated for width.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

from bs4 import BeautifulSoup
from django.conf import settings

from ..exceptions import SourceUnavailable, StructureChanged
from ..normalize import clean_team_display_name

logger = logging.getLogger(__name__)

PROVIDER = "live"

# How the source labels a match's state, mapped onto Fixture.status.
_ENDED = {"ended", "ft", "aet", "finished", "full time"}
_IN_PLAY = {"firsthalf", "secondhalf", "halftime", "extratime", "penalties", "live"}
_NOT_STARTED = {"notstarted", "scheduled", "upcoming"}
_ABANDONED = {"postponed", "cancelled", "abandoned", "suspended"}

_SCORE = re.compile(r"^\s*(\d{1,2})\s*[-–]\s*(\d{1,2})\s*$")
# A row that shows a kick-off time instead of a state has not started.
_CLOCK = re.compile(r"^\s*\d{1,2}[:.]\d{2}\s*(am|pm)?\s*$", re.IGNORECASE)
_MINUTE = re.compile(r"(\d{1,3})\s*'")


class LiveSourceNotConfigured(RuntimeError):
    """SCRAPER_LIVE_* is missing from the environment."""


def base_url() -> str:
    value = getattr(settings, "SCRAPER_LIVE_BASE_URL", "")
    if not value:
        raise LiveSourceNotConfigured(
            "SCRAPER_LIVE_BASE_URL is not set; add it to .env / .env.prod "
            "(see .env.example) and restart the worker"
        )
    return value if value.endswith("/") else value + "/"


def scores_url() -> str:
    path = getattr(settings, "SCRAPER_LIVE_PATH", "").lstrip("/")
    if not path:
        raise LiveSourceNotConfigured("SCRAPER_LIVE_PATH is not set")
    return base_url() + path


def competition() -> str:
    value = getattr(settings, "SCRAPER_LIVE_COMPETITION", "")
    if not value:
        raise LiveSourceNotConfigured("SCRAPER_LIVE_COMPETITION is not set")
    return value


@dataclass(frozen=True)
class LiveMatch:
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    status: str  # "upcoming" | "live" | "completed" | "postponed"
    raw_status: str
    minute: Optional[int]
    kickoff_text: str
    match_date: Optional[date]

    @property
    def is_played(self) -> bool:
        return self.home_score is not None and self.away_score is not None


def _status_for(raw: str) -> str:
    value = (raw or "").strip().lower()
    if value in _ENDED:
        return "completed"
    if value in _ABANDONED:
        return "postponed"
    if value in _NOT_STARTED:
        return "upcoming"
    if value in _IN_PLAY or _MINUTE.search(value):
        return "live"
    if _CLOCK.match(value):
        return "upcoming"
    # An unrecognised label is reported rather than guessed at, because turning
    # an unknown state into "completed" would settle a match that is still on.
    logger.info("unrecognised match state %r; treating as upcoming", raw)
    return "upcoming"


def _parse_date(
    text: str, *, today: Optional[date] = None, finished: bool = False
) -> Optional[date]:
    """'May 31' -> a date. The source omits the year.

    The year is settled by the match's own state rather than by how far away the
    date is: a season's results page spans about ten months, so any fixed window
    mis-reads one end of it. A match that has ended cannot be in the future, and
    one still to be played cannot be well in the past.
    """
    text = (text or "").strip()
    if not text:
        return None
    today = today or date.today()

    for fmt in ("%b %d", "%d %b", "%B %d", "%d %B"):
        try:
            parsed = datetime.strptime(text, fmt).date()
        except ValueError:
            continue

        try:
            candidate = parsed.replace(year=today.year)
        except ValueError:  # 29 February in a common year
            candidate = parsed.replace(year=today.year, day=28)

        if finished and candidate > today:
            candidate = candidate.replace(year=today.year - 1)
        elif not finished and (today - candidate).days > 30:
            candidate = candidate.replace(year=today.year + 1)
        return candidate
    return None


def _club_name(cell) -> str:
    """Read a club name from a team cell, preferring the logo's alt text."""
    logo = cell.find("img")
    if logo and logo.get("alt", "").strip():
        return clean_team_display_name(logo["alt"])
    return clean_team_display_name(cell.get_text(" ", strip=True))


def parse_scores(html: str, *, today: Optional[date] = None) -> List[LiveMatch]:
    """Parse the rendered scores DOM into matches.

    Kept separate from the browser so it can be tested against saved markup.
    """
    soup = BeautifulSoup(html, "lxml")

    rows = [
        row
        for row in soup.select("div.grid.grid-cols-12")
        if row.select_one("div.col-span-2") and row.find("img")
    ]
    if not rows:
        raise StructureChanged(
            "the live scores page rendered no match rows; the markup has moved "
            "or the competition filter matched nothing"
        )

    matches: List[LiveMatch] = []
    for row in rows:
        cells = row.find_all("div", recursive=False)
        if len(cells) < 4:
            continue

        meta, home_cell, score_cell, away_cell = cells[0], cells[1], cells[2], cells[3]

        meta_lines = [
            line for line in meta.get_text("\n", strip=True).split("\n") if line.strip()
        ]
        date_text = meta_lines[0] if meta_lines else ""
        raw_status = meta_lines[1] if len(meta_lines) > 1 else ""

        home = _club_name(home_cell)
        away = _club_name(away_cell)
        if not home or not away:
            continue

        middle = score_cell.get_text(" ", strip=True)
        score = _SCORE.match(middle)
        home_score = int(score.group(1)) if score else None
        away_score = int(score.group(2)) if score else None

        minute_match = _MINUTE.search(raw_status) or _MINUTE.search(middle)
        status = _status_for(raw_status)

        matches.append(
            LiveMatch(
                home_team=home,
                away_team=away,
                home_score=home_score,
                away_score=away_score,
                status=status,
                raw_status=raw_status,
                minute=int(minute_match.group(1)) if minute_match else None,
                kickoff_text="" if score else middle,
                match_date=_parse_date(
                    date_text, today=today, finished=status == "completed"
                ),
            )
        )

    logger.info("parsed %d live rows", len(matches))
    return matches


def fetch_scores(*, driver=None, settle_seconds: int = 8) -> List[LiveMatch]:
    """Render the scores page, filter it to the configured competition, parse it.

    ``driver`` lets a caller reuse an open browser; without one a session is
    opened and closed here.
    """
    from util.selenium import SeleniumManager

    manager = None
    if driver is None:
        manager = SeleniumManager()
        driver = manager.get_driver()
        if driver is None:
            raise SourceUnavailable("no browser available for the live scores page")

    try:
        driver.get(scores_url())
        # The shell loads instantly and the matches arrive afterwards, so there
        # is nothing to wait on but time.
        _wait(settle_seconds)

        if not _apply_competition_filter(driver, competition()):
            raise StructureChanged(
                f"no {competition()!r} filter on the live scores page; the "
                "competition may be named differently or not be in season"
            )
        _wait(4)
        return parse_scores(driver.page_source)
    finally:
        if manager is not None:
            manager.close()


def _wait(seconds: int) -> None:
    import time

    time.sleep(seconds)


def _apply_competition_filter(driver, label: str) -> bool:
    """Click the competition in the page's own filter list.

    The page shows every competition it covers on one screen; filtering to ours
    is both cheaper to parse and avoids mistaking a cup or a youth fixture
    between the same two clubs for a league match.
    """
    from selenium.webdriver.common.by import By

    for element in driver.find_elements(By.CSS_SELECTOR, "div.cursor-pointer"):
        try:
            if element.text.strip().casefold() == label.casefold():
                driver.execute_script("arguments[0].click();", element)
                return True
        except Exception:  # noqa: BLE001 - a stale node just means keep looking
            continue
    return False
