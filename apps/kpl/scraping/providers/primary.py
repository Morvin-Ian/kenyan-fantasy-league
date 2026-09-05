"""Primary data provider.

The source is a plain server-rendered site with no bot protection and no
JavaScript, so every page here is read with a single HTTP GET — no Selenium, no
headless browser.

Nothing in this module names the source. The base URL, the competition label and
every page path come from the environment (``SCRAPER_PRIMARY_*`` in
``config.settings.base``), so the repository never records where the data comes
from and a source can be swapped without touching code.

Page roles, named by the keys of ``SCRAPER_PRIMARY_PATHS``:

==============  ==========================================================
``index``       every competition the source covers, used to discover the
                current season id
``teams``       the competing clubs and their badge files
``standings``   the league table
``fixtures``    scheduled matches, grouped by date
``results``     played matches with final scores, grouped by matchday
``scorers``     the scoring charts
``squads``      every registered squad, on one page
``match``       one played match: goals with minutes, both lineups and
                benches, and cards
==============  ==========================================================

``index``/``teams``/… take a ``{season}`` placeholder, ``match`` takes
``{match}``. The source's own opaque ids for competitions, clubs, players and
matches are carried through untouched and reused as ``External*Mapping`` keys,
which is what makes every sync idempotent.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.conf import settings

from ..exceptions import ParseError, SeasonNotFound, StructureChanged
from ..http import fetch
from ..normalize import clean_player_name, clean_team_display_name

logger = logging.getLogger(__name__)

PROVIDER = "primary"
# Match reports are numbered separately from scheduled fixtures, so their ids
# need their own mapping namespace.
MATCH_PROVIDER = "primary:match"


class SourceNotConfigured(RuntimeError):
    """SCRAPER_PRIMARY_* is missing from the environment."""


def base_url() -> str:
    value = getattr(settings, "SCRAPER_PRIMARY_BASE_URL", "")
    if not value:
        raise SourceNotConfigured(
            "SCRAPER_PRIMARY_BASE_URL is not set; add it to .env / .env.prod "
            "(see .env.example) and restart the worker"
        )
    return value if value.endswith("/") else value + "/"


def _paths() -> Dict[str, str]:
    """Parse ``SCRAPER_PRIMARY_PATHS`` into ``{role: path template}``.

    Format is a comma-separated list of ``role=path`` pairs, for example::

        SCRAPER_PRIMARY_PATHS=index=a.php,standings=b.php?t={season}
    """
    raw = getattr(settings, "SCRAPER_PRIMARY_PATHS", "")
    paths = {}
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        role, _, template = chunk.partition("=")
        paths[role.strip()] = template.strip()
    return paths


def path_for(role: str, **params) -> str:
    """Build the absolute URL for a page role."""
    template = _paths().get(role)
    if not template:
        raise SourceNotConfigured(
            f"no '{role}' entry in SCRAPER_PRIMARY_PATHS; expected a "
            f"'{role}=<path>' pair in that variable"
        )
    return urljoin(base_url(), template.format(**params))


def _season_label_pattern() -> re.Pattern:
    """Match "<Competition> YYYY/YYYY" and nothing more.

    The trailing anchor matters: the source also lists a promotion/relegation
    play-off whose label starts with the same words, and picking that up would
    scrape the wrong competition.
    """
    competition = getattr(settings, "SCRAPER_PRIMARY_COMPETITION", "")
    if not competition:
        raise SourceNotConfigured("SCRAPER_PRIMARY_COMPETITION is not set")
    return re.compile(
        rf"^{re.escape(competition)}\s+(\d{{4}})/(\d{{4}})\s*$", re.IGNORECASE
    )


# Ids are read out of link targets. Competition and club links share the same
# query parameter, so they are told apart by the page they point at rather than
# by any id prefix — that keeps the source's naming scheme out of this file.
_COMPETITION_ID = re.compile(r"[?&]t=([A-Za-z0-9_-]+)")
_TEAM_ID = re.compile(r"(?:^|/)team[a-z_]*\.[a-z]+\?(?:[^&]*&)*t=([A-Za-z0-9_-]+)")
_PLAYER_ID = re.compile(
    r"(?:^|/)player[a-z_]*\.[a-z]+\?(?:[^&]*&)*[pd]=([A-Za-z0-9_-]+)"
)
_FIXTURE_ID = re.compile(r"(?:^|/)fixture[a-z_]*\.[a-z]+\?(?:[^&]*&)*f=(\d+)")
_MATCH_ID = re.compile(r"(?:^|/)score[a-z_]*\.[a-z]+\?(?:[^&]*&)*s=(\d+)")
_TEAM_LINK = re.compile(r"(?:^|/)team[a-z_]*\.[a-z]+\?")
_SQUAD_LINK = re.compile(r"(?:^|/)team_players\.[a-z]+\?")
_COMPETITION_LINK = re.compile(r"(?:^|/)tournament\.[a-z]+\?")
_MATCH_LINK = re.compile(r"(?:^|/)(?:fixture|score)[a-z_]*\.[a-z]+\?")

_MATCHDAY = re.compile(r"^(?:Matchday|Round)\s+(\w+)", re.IGNORECASE)
_DATE_HEADING = re.compile(
    r"^(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,\s*(\d{1,2})(?:st|nd|rd|th)\s+"
    r"([A-Za-z]+)\s+(\d{2,4})$"
)
_SCORELINE = re.compile(r"^(\d{1,2})\s*[-–]\s*(\d{1,2})$")
_MINUTE = re.compile(r"(\d{1,3})\s*'")

_WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


# --------------------------------------------------------------------------- #
# Result types
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Season:
    tournament_id: str
    label: str
    start_year: int
    end_year: int


@dataclass(frozen=True)
class TeamRow:
    provider_id: str
    name: str
    logo_url: Optional[str]
    county: Optional[str] = None


@dataclass(frozen=True)
class StandingRow:
    position: int
    provider_team_id: Optional[str]
    team_name: str
    logo_url: Optional[str]
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_differential: int
    points: int


@dataclass(frozen=True)
class FixtureRow:
    provider_fixture_id: Optional[str]
    provider_score_id: Optional[str]
    matchday: Optional[int]
    kickoff: datetime
    has_kickoff_time: bool
    home_team: str
    away_team: str
    home_provider_id: Optional[str]
    away_provider_id: Optional[str]
    venue: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None

    @property
    def is_played(self) -> bool:
        return self.home_score is not None and self.away_score is not None


@dataclass(frozen=True)
class ScorerRow:
    rank: int
    player_name: str
    provider_player_id: Optional[str]
    team_name: str
    provider_team_id: Optional[str]
    goals: int


@dataclass(frozen=True)
class SquadPlayer:
    provider_player_id: Optional[str]
    name: str
    shirt_role: str = ""


@dataclass(frozen=True)
class Squad:
    provider_team_id: str
    team_name: str
    logo_url: Optional[str]
    players: List[SquadPlayer] = field(default_factory=list)


@dataclass(frozen=True)
class MatchGoal:
    team_side: str  # "home" | "away"
    player_name: str
    minute: Optional[int]


@dataclass(frozen=True)
class MatchCard:
    team_name: str
    player_name: str
    card: str  # "yellow" | "red"
    minute: Optional[int]


@dataclass(frozen=True)
class MatchDetail:
    provider_score_id: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    kickoff: Optional[datetime]
    venue: str
    goals: List[MatchGoal] = field(default_factory=list)
    cards: List[MatchCard] = field(default_factory=list)
    home_starters: List[str] = field(default_factory=list)
    away_starters: List[str] = field(default_factory=list)
    home_bench: List[str] = field(default_factory=list)
    away_bench: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def _page(role: str, **params) -> str:
    """Absolute URL for a page role (see SCRAPER_PRIMARY_PATHS)."""
    return path_for(role, **params)


def _absolute_asset(src: Optional[str]) -> Optional[str]:
    if not src:
        return None
    src = src.strip()
    if src.startswith(("http://", "https://")):
        return src
    return urljoin(base_url(), src.lstrip("./"))


def _first_id(pattern: re.Pattern, element) -> Optional[str]:
    """Return the first id matching ``pattern`` in any href under ``element``."""
    if element is None:
        return None
    for anchor in element.find_all("a", href=True):
        match = pattern.search(anchor["href"])
        if match:
            return match.group(1)
    return None


def _int(value: str, *, field_name: str) -> int:
    """Parse an integer cell, tolerating the '+28' / '-3' goal-difference form."""
    text = (value or "").strip().replace("+", "")
    if not text or text == "-":
        return 0
    try:
        return int(text)
    except ValueError as exc:
        raise ParseError(
            f"expected an integer for {field_name}, got {value!r}"
        ) from exc


def _matchday_number(caption: str) -> Optional[int]:
    """'Matchday 12' -> 12, 'Round Six' -> 6."""
    match = _MATCHDAY.match(caption.strip())
    if not match:
        return None
    token = match.group(1)
    if token.isdigit():
        return int(token)
    return _WORD_NUMBERS.get(token.lower())


def _parse_heading_date(text: str) -> Optional[date]:
    """'Sat, 29th Aug 26' -> date(2026, 8, 29)."""
    match = _DATE_HEADING.match(text.strip())
    if not match:
        return None
    day, month_name, year = match.groups()
    year_value = int(year)
    if year_value < 100:
        year_value += 2000
    for fmt in ("%b", "%B"):
        try:
            month = datetime.strptime(
                month_name[:3] if fmt == "%b" else month_name, fmt
            ).month
        except ValueError:
            continue
        return date(year_value, month, int(day))
    return None


def _parse_venue_cell(text: str) -> tuple[Optional[time], str]:
    """'15:00,  Kasarani International Stadium' -> (15:00, 'Kasarani ...').

    The site is inconsistent about the separator and sometimes prefixes the venue
    with a 'Derby' marker, so both are handled leniently.
    """
    raw = re.sub(r"\s+", " ", (text or "").strip())
    kickoff = None
    time_match = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)?", raw, re.IGNORECASE)
    if time_match:
        hour, minute, meridiem = time_match.groups()
        hour, minute = int(hour), int(minute)
        if meridiem:
            meridiem = meridiem.upper()
            if meridiem == "PM" and hour != 12:
                hour += 12
            elif meridiem == "AM" and hour == 12:
                hour = 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            kickoff = time(hour, minute)
        raw = raw[time_match.end() :]

    venue = raw.lstrip(" ,").strip()
    venue = re.sub(r"^Derby\b\s*", "", venue, flags=re.IGNORECASE).strip()
    return kickoff, venue or "Unknown"


def _is_match_row(row) -> bool:
    """A match row has a team link on each side of a Vs / scoreline cell."""
    return len(row.find_all("a", href=_TEAM_LINK)) == 2


# --------------------------------------------------------------------------- #
# Season discovery
# --------------------------------------------------------------------------- #


def discover_current_season() -> Season:
    """Find the newest ``Kenya Premier League YYYY/YYYY`` tournament id.

    Discovery beats a hard-coded id: the tournament id changes every season
    every season, and a stale constant silently scrapes last season's finished
    data instead of failing.
    """
    index_url = _page("index")
    response = fetch(index_url)
    if response.not_modified:
        # Conditional GET only returns 304 when we have already seen this page;
        # re-fetch unconditionally so discovery always yields a value.
        response = fetch(index_url, use_conditional=False)

    label_pattern = _season_label_pattern()
    soup = _soup(response.text)
    seasons: List[Season] = []
    for anchor in soup.find_all("a", href=_COMPETITION_LINK):
        label = anchor.get_text(" ", strip=True)
        match = label_pattern.match(label)
        if not match:
            continue
        id_match = _COMPETITION_ID.search(anchor["href"])
        if not id_match:
            continue
        seasons.append(
            Season(
                tournament_id=id_match.group(1),
                label=label,
                start_year=int(match.group(1)),
                end_year=int(match.group(2)),
            )
        )

    if not seasons:
        raise SeasonNotFound(
            f"no '{settings.SCRAPER_PRIMARY_COMPETITION} YYYY/YYYY' entry found "
            "on the competition index; check SCRAPER_PRIMARY_COMPETITION matches "
            "the label the source uses, and that the index layout has not changed"
        )

    season = max(seasons, key=lambda s: s.start_year)
    logger.info(
        "discovered current season %s (%s) out of %d candidates",
        season.label,
        season.tournament_id,
        len(seasons),
    )
    return season


# --------------------------------------------------------------------------- #
# Teams and logos
# --------------------------------------------------------------------------- #


def fetch_teams(tournament_id: str) -> List[TeamRow]:
    """Return every club in the tournament with its logo URL."""
    response = fetch(_page("teams", season=tournament_id), use_conditional=False)
    soup = _soup(response.text)

    teams: Dict[str, TeamRow] = {}
    for row in soup.find_all("tr"):
        anchor = row.find("a", href=_TEAM_ID)
        if not anchor:
            continue
        team_id = _TEAM_ID.search(anchor["href"]).group(1)
        if team_id in teams:
            continue
        image = row.find("img")
        cells = row.find_all("td")
        county = cells[-1].get_text(" ", strip=True) if len(cells) >= 4 else None
        teams[team_id] = TeamRow(
            provider_id=team_id,
            name=clean_team_display_name(anchor.get_text(" ", strip=True)),
            logo_url=_absolute_asset(image.get("src") if image else None),
            county=county or None,
        )

    if not teams:
        raise StructureChanged(
            f"the teams page for season {tournament_id} yielded no clubs; "
            "expected rows linking to a club page"
        )
    logger.info("parsed %d clubs for %s", len(teams), tournament_id)
    return sorted(teams.values(), key=lambda t: t.name)


# --------------------------------------------------------------------------- #
# League table
# --------------------------------------------------------------------------- #

# 0:# 1:logo 2:Team 3:(blank) 4:GP 5:W 6:D 7:L 8:F 9:A 10:GD 11:P
_STANDINGS_COLUMNS = 12


def fetch_standings(tournament_id: str) -> List[StandingRow]:
    """Parse the league table.

    Returns an empty list when the season has started but no results are in yet
    — that is a legitimate state, not a failure. A malformed table raises
    :class:`StructureChanged` so a layout change never masquerades as "no data".
    """
    response = fetch(_page("standings", season=tournament_id), use_conditional=False)
    soup = _soup(response.text)

    table = soup.find("table")
    if table is None:
        raise StructureChanged(
            f"the standings page for season {tournament_id} contains no <table>"
        )

    rows = table.find_all("tr")
    header = rows[0].find_all(["th", "td"]) if rows else []
    if len(header) != _STANDINGS_COLUMNS:
        raise StructureChanged(
            f"league table header has {len(header)} columns, expected "
            f"{_STANDINGS_COLUMNS} (#, logo, Team, _, GP, W, D, L, F, A, GD, P)"
        )

    standings: List[StandingRow] = []
    for index, row in enumerate(rows[1:], start=1):
        cells = row.find_all("td")
        if len(cells) != _STANDINGS_COLUMNS:
            logger.debug("skipping table row %d with %d cells", index, len(cells))
            continue

        position_text = cells[0].get_text(strip=True).rstrip(".")
        if not position_text.isdigit():
            continue

        image = cells[1].find("img")
        team_anchor = cells[2].find("a")
        team_name = clean_team_display_name(
            (team_anchor or cells[2]).get_text(" ", strip=True)
        )
        if not team_name:
            continue

        standings.append(
            StandingRow(
                position=int(position_text),
                provider_team_id=_first_id(_TEAM_ID, cells[2]),
                team_name=team_name,
                logo_url=_absolute_asset(image.get("src") if image else None),
                played=_int(cells[4].get_text(), field_name="played"),
                wins=_int(cells[5].get_text(), field_name="wins"),
                draws=_int(cells[6].get_text(), field_name="draws"),
                losses=_int(cells[7].get_text(), field_name="losses"),
                goals_for=_int(cells[8].get_text(), field_name="goals_for"),
                goals_against=_int(cells[9].get_text(), field_name="goals_against"),
                goal_differential=_int(cells[10].get_text(), field_name="goal_diff"),
                points=_int(cells[11].get_text(), field_name="points"),
            )
        )

    logger.info("parsed %d standings rows for %s", len(standings), tournament_id)
    return standings


# --------------------------------------------------------------------------- #
# Fixtures and results
# --------------------------------------------------------------------------- #


def _parse_match_tables(html: str, *, with_scores: bool) -> List[FixtureRow]:
    """Walk the matchday tables on a fixtures or scores page.

    Both pages share one layout: a stack of tables, each captioned with a
    matchday, containing date headings followed by the match rows for that date.
    """
    soup = _soup(html)
    fixtures: List[FixtureRow] = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        matchday = _matchday_number(rows[0].get_text(" ", strip=True))
        current_date: Optional[date] = None

        for row in rows:
            text = row.get_text(" ", strip=True)

            heading_date = _parse_heading_date(text)
            if heading_date is not None:
                current_date = heading_date
                continue

            if not _is_match_row(row):
                continue

            anchors = row.find_all("a", href=_TEAM_LINK)
            home_anchor, away_anchor = anchors[0], anchors[1]

            middle = row.find("a", href=_MATCH_LINK)
            middle_text = middle.get_text(" ", strip=True) if middle else ""
            home_score = away_score = None
            score_match = _SCORELINE.match(middle_text)
            if score_match:
                home_score = int(score_match.group(1))
                away_score = int(score_match.group(2))
            elif with_scores:
                # A scores page row without a scoreline is not a played match.
                continue

            # Only the fixtures page carries a venue cell. On the scores page
            # there is none, and falling back to a positional cell would pick up
            # the away club's name as the venue.
            venue_cell = row.find("td", class_="venue")
            kickoff_time, venue = _parse_venue_cell(
                venue_cell.get_text(" ", strip=True) if venue_cell else ""
            )
            if venue_cell is None:
                venue = ""

            if current_date is None:
                logger.debug(
                    "match row before any date heading; skipping: %s", text[:80]
                )
                continue

            has_time = kickoff_time is not None
            kickoff = datetime.combine(current_date, kickoff_time or time(15, 0))

            href = middle["href"] if middle else ""
            fixture_match = _FIXTURE_ID.search(href)
            score_id_match = _MATCH_ID.search(href)

            fixtures.append(
                FixtureRow(
                    provider_fixture_id=(
                        fixture_match.group(1) if fixture_match else None
                    ),
                    provider_score_id=(
                        score_id_match.group(1) if score_id_match else None
                    ),
                    matchday=matchday,
                    kickoff=kickoff,
                    has_kickoff_time=has_time,
                    home_team=clean_team_display_name(
                        home_anchor.get_text(" ", strip=True)
                    ),
                    away_team=clean_team_display_name(
                        away_anchor.get_text(" ", strip=True)
                    ),
                    home_provider_id=(
                        _TEAM_ID.search(home_anchor["href"]).group(1)
                        if _TEAM_ID.search(home_anchor["href"])
                        else None
                    ),
                    away_provider_id=(
                        _TEAM_ID.search(away_anchor["href"]).group(1)
                        if _TEAM_ID.search(away_anchor["href"])
                        else None
                    ),
                    venue=venue,
                    home_score=home_score,
                    away_score=away_score,
                )
            )

    return _dedupe(fixtures)


def _dedupe(fixtures: List[FixtureRow]) -> List[FixtureRow]:
    """Collapse rows that the source lists twice.

    The scores page repeats recent results in trailing date-only tables as well
    as in their numbered matchday table. Keep one row per provider id, and
    prefer the copy that knows its matchday.
    """
    best: Dict[str, FixtureRow] = {}
    unkeyed: List[FixtureRow] = []

    for fixture in fixtures:
        key = fixture.provider_score_id or fixture.provider_fixture_id
        if key is None:
            unkeyed.append(fixture)
            continue
        existing = best.get(key)
        if existing is None or (
            existing.matchday is None and fixture.matchday is not None
        ):
            best[key] = fixture

    return sorted(
        [*best.values(), *unkeyed],
        key=lambda f: (f.kickoff, f.home_team),
    )


def fetch_fixtures(tournament_id: str) -> List[FixtureRow]:
    """Scheduled matches, grouped by matchday, with kickoff time and venue."""
    response = fetch(_page("fixtures", season=tournament_id), use_conditional=False)
    fixtures = _parse_match_tables(response.text, with_scores=False)
    logger.info("parsed %d fixtures for %s", len(fixtures), tournament_id)
    return fixtures


def fetch_results(tournament_id: str) -> List[FixtureRow]:
    """Played matches with their final scores and their match-report ids."""
    response = fetch(_page("results", season=tournament_id), use_conditional=False)
    results = _parse_match_tables(response.text, with_scores=True)
    logger.info("parsed %d results for %s", len(results), tournament_id)
    return results


# --------------------------------------------------------------------------- #
# Top scorers
# --------------------------------------------------------------------------- #


def fetch_scorers(
    tournament_id: str, *, limit: Optional[int] = None
) -> List[ScorerRow]:
    """Top scorers, highest first.

    The page carries two tables: goals scored, then own goals. Only the first is
    read — an own goal is not a fantasy return for the scorer.
    """
    response = fetch(_page("scorers", season=tournament_id), use_conditional=False)
    soup = _soup(response.text)

    tables = soup.find_all("table")
    if not tables:
        raise StructureChanged(
            f"the scorers page for season {tournament_id} contains no <table>"
        )

    scorers: List[ScorerRow] = []
    for row in tables[0].find_all("tr"):
        cells = row.find_all("td")
        if len(cells) != 4:
            continue

        rank_text = cells[0].get_text(strip=True).rstrip(".")
        if not rank_text.isdigit():
            continue

        player_name = clean_player_name(cells[1].get_text(" ", strip=True))
        if not player_name:
            continue

        goals_text = cells[3].get_text(strip=True)
        if not goals_text.isdigit():
            continue

        scorers.append(
            ScorerRow(
                rank=int(rank_text),
                player_name=player_name,
                provider_player_id=_first_id(_PLAYER_ID, cells[1]),
                team_name=clean_team_display_name(cells[2].get_text(" ", strip=True)),
                provider_team_id=_first_id(_TEAM_ID, cells[2]),
                goals=int(goals_text),
            )
        )

    scorers.sort(key=lambda s: (-s.goals, s.player_name))
    logger.info("parsed %d scorers for %s", len(scorers), tournament_id)
    return scorers[:limit] if limit else scorers


# --------------------------------------------------------------------------- #
# Squads
# --------------------------------------------------------------------------- #


def fetch_squads(tournament_id: str) -> List[Squad]:
    """Every squad in the tournament, from the single combined players page.

    One request returns all ~1100 registered players, so there is no need to walk
    per-club pages. Note the source does not publish positions or ages; those
    stay under whatever the application already holds.
    """
    response = fetch(_page("squads", season=tournament_id), use_conditional=False)
    soup = _soup(response.text)

    squads: List[Squad] = []
    for anchor in soup.find_all("a", href=_SQUAD_LINK):
        id_match = _TEAM_ID.search(anchor["href"])
        if not id_match:
            continue

        team_name = clean_team_display_name(anchor.get_text(" ", strip=True))
        logo_image = anchor.find_previous("img", class_="logo")
        table = anchor.find_next("table")
        if table is None:
            logger.warning("no squad table after club heading %s", team_name)
            continue

        players: List[SquadPlayer] = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            player_anchor = cells[2].find("a", href=_PLAYER_ID)
            if not player_anchor:
                continue
            name = clean_player_name(player_anchor.get_text(" ", strip=True))
            if not name:
                continue
            players.append(
                SquadPlayer(
                    provider_player_id=_PLAYER_ID.search(player_anchor["href"]).group(
                        1
                    ),
                    name=name,
                    shirt_role=cells[1].get_text(strip=True),
                )
            )

        squads.append(
            Squad(
                provider_team_id=id_match.group(1),
                team_name=team_name,
                logo_url=_absolute_asset(logo_image.get("src") if logo_image else None),
                players=players,
            )
        )

    if not squads:
        raise StructureChanged(
            f"the squads page for season {tournament_id} yielded no squads"
        )
    logger.info(
        "parsed %d squads / %d players for %s",
        len(squads),
        sum(len(s.players) for s in squads),
        tournament_id,
    )
    return squads


# --------------------------------------------------------------------------- #
# Match detail
# --------------------------------------------------------------------------- #


def fetch_match_detail(score_id: str) -> MatchDetail:
    """Parse a played match: scorers with minutes, both lineups, and cards.

    This replaces the browser-driven path for settling a finished match. It
    is published after the final whistle rather than live, so it is a settlement
    source, not an in-play one.
    """
    response = fetch(
        _page("match", match=score_id), use_conditional=False, min_bytes=800
    )
    soup = _soup(response.text)

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    title_match = re.match(r"^(.*?)\s+(\d{1,2})\s*[-–]\s*(\d{1,2})\s+(.*)$", title)
    if not title_match:
        raise StructureChanged(
            f"match report {score_id} has title {title!r}, "
            "which is not '<home> N - N <away>'"
        )
    home_team = clean_team_display_name(title_match.group(1))
    away_team = clean_team_display_name(title_match.group(4))
    home_score = int(title_match.group(2))
    away_score = int(title_match.group(3))

    tables = soup.find_all("table")
    goals: List[MatchGoal] = []
    kickoff: Optional[datetime] = None
    venue = "Unknown"

    if tables:
        header_rows = tables[0].find_all("tr")
        if header_rows:
            match_date = _parse_long_date(header_rows[0].get_text(" ", strip=True))
            if len(header_rows) >= 2:
                cells = header_rows[1].find_all("td")
                # The two middle cells hold "<club> <score> <scorer MM'> ..." per side.
                sides = [c for c in cells if c.get_text(strip=True)]
                for side_name, cell in zip(("home", "away"), sides[:2]):
                    goals.extend(_parse_goal_cell(cell, side_name))
            if len(header_rows) >= 3:
                kickoff_time, venue = _parse_venue_cell(
                    header_rows[2].get_text(" ", strip=True)
                )
                if match_date is not None:
                    kickoff = datetime.combine(match_date, kickoff_time or time(15, 0))
            elif match_date is not None:
                kickoff = datetime.combine(match_date, time(15, 0))

    home_starters, away_starters = _parse_lineup_table(
        tables[1] if len(tables) > 1 else None
    )
    home_bench, away_bench = _parse_lineup_table(tables[2] if len(tables) > 2 else None)

    return MatchDetail(
        provider_score_id=str(score_id),
        home_team=home_team,
        away_team=away_team,
        home_score=home_score,
        away_score=away_score,
        kickoff=kickoff,
        venue=venue,
        goals=goals,
        cards=_parse_cards(soup),
        home_starters=home_starters,
        away_starters=away_starters,
        home_bench=home_bench,
        away_bench=away_bench,
    )


def _parse_long_date(text: str) -> Optional[date]:
    """'Sunday 31st May 2026' -> date(2026, 5, 31)."""
    cleaned = re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", (text or "").strip())
    for fmt in ("%A %d %B %Y", "%A %d %b %Y", "%A %d %B %y", "%A %d %b %y"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def _parse_goal_cell(cell, side: str) -> List[MatchGoal]:
    """Pull ``"Victor OMONDI OTIENO 91'"`` entries out of one side's summary cell."""
    goals: List[MatchGoal] = []
    for line in cell.get_text("\n", strip=True).split("\n"):
        line = line.strip()
        minute_match = _MINUTE.search(line)
        if not minute_match:
            continue
        name = clean_player_name(line[: minute_match.start()])
        if not name:
            continue
        goals.append(
            MatchGoal(
                team_side=side, player_name=name, minute=int(minute_match.group(1))
            )
        )
    return goals


def _parse_lineup_table(table) -> tuple[List[str], List[str]]:
    """Read a two-column ``# | home player | away player`` lineup table."""
    home: List[str] = []
    away: List[str] = []
    if table is None:
        return home, away

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        index = cells[0].get_text(strip=True).rstrip(".")
        if not index.isdigit():
            continue
        home_name = clean_player_name(cells[1].get_text(" ", strip=True))
        away_name = clean_player_name(cells[2].get_text(" ", strip=True))
        if home_name:
            home.append(home_name)
        if away_name:
            away.append(away_name)
    return home, away


def _parse_cards(soup: BeautifulSoup) -> List[MatchCard]:
    """Read the Cautions block.

    Each caution is one anchor carrying its colour as a CSS class::

        <a class='list-group-item yellowcard'>
            1. <b>Yellow Card</b> - David SAKWA NYONGESA 50' - KCB FC
        </a>
    """
    cards: List[MatchCard] = []

    for anchor in soup.select("a.list-group-item"):
        classes = " ".join(anchor.get("class") or [])
        if "yellowcard" in classes:
            colour = "yellow"
        elif "redcard" in classes:
            colour = "red"
        else:
            continue

        text = re.sub(r"\s+", " ", anchor.get_text(" ", strip=True))
        # Drop the leading "1." index and the "<colour> Card" label.
        body = re.sub(r"^\s*\d+\s*\.\s*", "", text)
        body = re.sub(r"^(Yellow|Red)\s+Card\s*-?\s*", "", body, flags=re.IGNORECASE)

        parts = [part.strip() for part in body.split(" - ") if part.strip()]
        if not parts:
            continue

        player_part = parts[0]
        team_part = parts[1] if len(parts) > 1 else ""
        minute_match = _MINUTE.search(player_part)
        player_name = clean_player_name(
            player_part[: minute_match.start()] if minute_match else player_part
        )
        if not player_name:
            continue

        cards.append(
            MatchCard(
                team_name=clean_team_display_name(team_part),
                player_name=player_name,
                card=colour,
                minute=int(minute_match.group(1)) if minute_match else None,
            )
        )

    return cards
