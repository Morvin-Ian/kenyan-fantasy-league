"""Pre-match lineup fetching.

Only fires for fixtures whose provider match-page URL has been mapped; without a
mapping there is nothing to fetch. The remaining adapter reads static HTML, so
no browser is involved.
"""

import json
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from apps.kpl.models import ExternalFixtureMapping, Fixture
from apps.kpl.scrapers import scrape_lineups_for_url
from apps.kpl.services import upsert_fixture_lineup
from config.settings import base as settings

logger = logging.getLogger(__name__)


@dataclass
class ParsedLineup:
    formation: Optional[str]
    is_confirmed: bool
    published_at: Optional[datetime]
    starters: List[Dict]
    bench: List[Dict]


def _providers() -> List[str]:
    """Lineup providers to try, in order, from SCRAPER_LINEUP_PROVIDERS.

    Kept in the environment rather than the source tree so the repository does
    not record which sites this project reads.
    """
    raw = getattr(settings, "SCRAPER_LINEUP_PROVIDERS", "") or ""
    return [tag.strip() for tag in raw.split(",") if tag.strip()]


PROVIDERS = _providers()


def build_lineup_url(provider: str, fixture: Fixture) -> Optional[str]:
    """The provider's match-page URL for this fixture, if one is mapped.

    There is no way to construct it: the mapping has to have been written by a
    sync that saw the fixture on the provider's own pages.
    """
    mapping = ExternalFixtureMapping.objects.filter(  # type: ignore[attr-defined]
        provider=provider, fixture=fixture
    ).first()
    if not mapping:
        return None
    value = mapping.provider_fixture_id
    return value if value.startswith(("http://", "https://")) else None


def parse_lineup_from_source(provider: str, url: str, *, side: str) -> Optional[ParsedLineup]:
    try:
        result = scrape_lineups_for_url(None, url)
    except Exception as exc:  # noqa: BLE001 - one bad provider must not stop the rest
        logger.warning("parse failed for %s: %s", provider, exc)
        return None

    dto = result.get(side)
    if not dto:
        return None
    return ParsedLineup(
        formation=dto.get("formation"),
        is_confirmed=dto.get("is_confirmed", True),
        published_at=dto.get("published_at"),
        starters=dto.get("starters", []),
        bench=dto.get("bench", []),
    )


def _with_backoff_attempts(max_attempts: int = 3):
    for attempt in range(1, max_attempts + 1):
        yield attempt, (2**attempt) + random.uniform(0, 1)


def fetch_lineup_for_fixture(fixture: Fixture) -> Tuple[bool, str]:
    if not settings.LINEUPS_SCRAPING_ENABLED:
        return False, "feature disabled"

    configured = _providers()
    providers = [settings.PRIMARY_LINEUP_SOURCE] + [
        p for p in configured if p != settings.PRIMARY_LINEUP_SOURCE
    ]

    for provider in providers:
        url = build_lineup_url(provider, fixture)
        if not url:
            continue

        for attempt, sleep_seconds in _with_backoff_attempts(3):
            for side, team in (("home", fixture.home_team), ("away", fixture.away_team)):
                result = parse_lineup_from_source(provider, url, side=side)
                if result is None:
                    continue
                upsert_fixture_lineup(
                    fixture=fixture,
                    team=team,
                    side=side,
                    source=provider,
                    formation=result.formation,
                    is_confirmed=result.is_confirmed,
                    published_at=result.published_at,
                    starters=result.starters,
                    bench=result.bench,
                )
                logger.info(
                    "Lineup saved for fixture %s (%s/%s) via %s",
                    fixture.id,
                    team.name,
                    side,
                    provider,
                )
            if fixture.lineups.exists():
                return True, "done"
            if attempt < 3:
                time.sleep(sleep_seconds)

    return True, "done"


@shared_task(
    autoretry_for=(Exception,), retry_backoff=30, retry_backoff_max=300, max_retries=5
)
def fetch_lineup_for_fixture_task(fixture_id: str) -> str:
    fixture = Fixture.objects.filter(id=fixture_id).select_related("home_team", "away_team").first()  # type: ignore[attr-defined]
    if not fixture:
        return f"fixture {fixture_id} not found"
    ok, msg = fetch_lineup_for_fixture(fixture)
    return f"{ok}: {msg}"


@shared_task(
    autoretry_for=(Exception,), retry_backoff=30, retry_backoff_max=300, max_retries=3
)
def scan_upcoming_fixtures_for_lineups() -> str:
    """Scan fixtures within the next 3 hours (and up to KO+5 minutes) and schedule lineup fetches.

    - Skips when LINEUPS_SCRAPING_ENABLED is false
    - Limits concurrent schedules to LINEUP_SCRAPER_MAX_CONCURRENCY
    - Stops trying after KO+5 minutes
    """
    if not settings.LINEUPS_SCRAPING_ENABLED:
        logger.info("LINEUPS_SCRAPING_ENABLED is false; skipping scan")
        return "disabled"

    now = timezone.now()
    window_end = now + timedelta(hours=3)
    ko_grace_start = now - timedelta(minutes=5)

    # Include fixtures that are:
    # - upcoming within next 3 hours, or
    # - already kicked off but within the first 5 minutes (KO+5)
    fixtures = (
        Fixture.objects.filter(
            match_date__lte=window_end, match_date__gte=ko_grace_start
        )
        .select_related("home_team", "away_team")
        .prefetch_related("lineups")
        .order_by("match_date")
    )

    scheduled = 0
    max_concurrency = max(
        1, int(getattr(settings, "LINEUP_SCRAPER_MAX_CONCURRENCY", 2))
    )

    def _schedule_clocked_fetches(fix: Fixture) -> int:
        offsets = [
            ("KO-90", timedelta(minutes=90)),
            ("KO-75", timedelta(minutes=75)),
            ("KO-60", timedelta(minutes=60)),
            ("KO-30", timedelta(minutes=30)),
            ("KO-15", timedelta(minutes=15)),
            ("KO-10", timedelta(minutes=10)),
            ("KO-5", timedelta(minutes=5)),
        ]
        created = 0
        for label, delta in offsets:
            run_at = fix.match_date - delta
            if run_at <= now:
                continue
            name = f"lineups:clocked:{fix.id}:{label}"
            clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=run_at)
            task, was_created = PeriodicTask.objects.get_or_create(
                name=name,
                defaults={
                    "task": "apps.kpl.tasks.lineups.fetch_lineup_for_fixture_task",
                    "one_off": True,
                    "clocked": clocked,
                    "args": json.dumps([str(fix.id)]),
                },
            )
            if was_created:
                created += 1
                logger.info(
                    "LINEUPS_SCRAPER clocked task created name=%s run_at=%s fixture=%s",
                    name,
                    run_at,
                    fix.id,
                )
        return created

    for fixture in fixtures:
        # Skip if both sides are confirmed
        lineups = fixture.lineups.all()  # type: ignore[attr-defined]
        has_home_confirmed = any(
            line.side == "home" and line.is_confirmed for line in lineups
        )
        has_away_confirmed = any(
            line.side == "away" and line.is_confirmed for line in lineups
        )
        if has_home_confirmed and has_away_confirmed:
            continue

        # Stop trying beyond KO+5
        if now > fixture.match_date + timedelta(minutes=5):
            continue

        try:
            fetch_lineup_for_fixture_task.delay(str(fixture.id))
        except Exception as e:
            logger.warning("LINEUPS_SCRAPER failed to schedule immediate fetch: %s", e)
            webhook = getattr(settings, "LINEUPS_ALERT_WEBHOOK", None)
            if webhook:
                logger.warning(
                    "LINEUPS_ALERT_WEBHOOK configured; consider sending alert"
                )
        scheduled += 1
        logger.info(
            "LINEUPS_SCRAPER scan scheduled fetch for fixture=%s at %s (scheduled=%s)",
            fixture.id,
            fixture.match_date,
            scheduled,
        )
        _schedule_clocked_fetches(fixture)
        if scheduled >= max_concurrency:
            break

    return f"scheduled={scheduled}"
