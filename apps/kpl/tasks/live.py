"""Live score updates from the browser-rendered scores source.

The settlement path (``sync_results`` / ``sync_match_details``) reads the primary
source, which publishes a match only after the final whistle. This task fills
the gap in between: it reads a page that updates while matches are being played,
so the site can show a score that is moving and the fantasy points can settle as
soon as a match ends rather than waiting for the report.

It is deliberately conservative about what it writes. A score only ever moves
onto a fixture the task could match with confidence, an unrecognised state is
treated as "still to play" rather than settling a live match, and a fixture that
the settlement path has already completed is left alone.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Dict, List, Optional

from django.utils import timezone

from apps.kpl.models import Fixture, Team
from apps.kpl.scraping import ScrapeError
from apps.kpl.scraping.normalize import team_key
from apps.kpl.scraping.providers import live

from .base import scraping_task

logger = logging.getLogger(__name__)

# How far from the scraped date a fixture may sit and still be the same match.
# Kick-offs move by a day; a week apart is a different fixture.
MATCH_WINDOW = timedelta(days=2)


def _team_index() -> Dict[str, Team]:
    return {team_key(team.name): team for team in Team.objects.all()}


def _resolve(name: str, index: Dict[str, Team]) -> Optional[Team]:
    return index.get(team_key(name))


@scraping_task(name="apps.kpl.tasks.live.sync_live_scores", lock_ttl=5 * 60)
def sync_live_scores():
    """Update in-play and just-finished fixtures from the live source."""
    try:
        matches = live.fetch_scores()
    except live.LiveSourceNotConfigured as exc:
        logger.warning("live scores are not configured: %s", exc)
        return {"success": False, "error": str(exc)}
    except ScrapeError as exc:
        logger.warning("live scores unavailable: %s", exc)
        return {"success": False, "error": str(exc)}

    index = _team_index()
    updated = completed = unmatched = 0
    unmatched_names: List[str] = []

    for match in matches:
        home = _resolve(match.home_team, index)
        away = _resolve(match.away_team, index)
        if home is None or away is None:
            unmatched += 1
            if len(unmatched_names) < 10:
                unmatched_names.append(f"{match.home_team} v {match.away_team}")
            continue

        fixture = _find_fixture(home, away, match)
        if fixture is None:
            unmatched += 1
            continue

        changed = []

        # The settlement path is the source of record for a finished match, so a
        # fixture it has already completed is never rewritten from here.
        if fixture.status == "completed" and match.status != "completed":
            continue

        if match.is_played:
            if fixture.home_team_score != match.home_score:
                fixture.home_team_score = match.home_score
                changed.append("home_team_score")
            if fixture.away_team_score != match.away_score:
                fixture.away_team_score = match.away_score
                changed.append("away_team_score")

        just_completed = False
        if match.status != fixture.status:
            fixture.status = match.status
            changed.append("status")
            if match.status == "completed":
                completed += 1
                just_completed = True

        if changed:
            fixture.save(update_fields=changed + ["updated_at"])
            updated += 1

            if just_completed:
                # Settle the clean sheets and goals conceded as soon as the
                # match ends, rather than waiting for the match report. The task
                # recomputes rather than accumulates, so the settlement path
                # running later over the same fixture is harmless.
                from apps.fantasy.tasks.fixture_completion import (
                    process_clean_sheets_on_completion,
                )

                process_clean_sheets_on_completion.delay(str(fixture.id))
            logger.info(
                "GW%s %s %s-%s %s [%s]",
                fixture.gameweek.number if fixture.gameweek else "?",
                home.name,
                match.home_score,
                match.away_score,
                away.name,
                match.raw_status,
            )

    if unmatched_names:
        logger.info("live rows with no fixture: %s", unmatched_names)

    return {
        "rows": len(matches),
        "fixtures_updated": updated,
        "fixtures_completed": completed,
        "unmatched": unmatched,
    }


def _find_fixture(home: Team, away: Team, match) -> Optional[Fixture]:
    """The scheduled fixture this row refers to, or None if it is ambiguous."""
    candidates = Fixture.objects.filter(home_team=home, away_team=away)

    if match.match_date is not None:
        start = timezone.make_aware(
            timezone.datetime.combine(
                match.match_date - MATCH_WINDOW, timezone.datetime.min.time()
            )
        )
        end = timezone.make_aware(
            timezone.datetime.combine(
                match.match_date + MATCH_WINDOW, timezone.datetime.max.time()
            )
        )
        candidates = candidates.filter(match_date__range=(start, end))
    else:
        # Without a date, only an in-play or imminent fixture is safe to touch.
        now = timezone.now()
        candidates = candidates.filter(
            match_date__range=(now - timedelta(hours=6), now + timedelta(hours=6))
        )

    found = list(candidates.select_related("gameweek", "home_team", "away_team")[:2])
    if len(found) != 1:
        return None
    return found[0]
