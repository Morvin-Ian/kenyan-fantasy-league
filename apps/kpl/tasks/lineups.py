import logging
import random
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple

from celery import shared_task
from django.db import transaction  # noqa: F401
from django.utils import timezone  # noqa: F401
# pyright: reportMissingTypeStubs=false, reportMissingImports=false, reportGeneralTypeIssues=false
from django_celery_beat.models import ClockedSchedule, PeriodicTask
# pyright: reportMissingTypeStubs=false, reportMissingImports=false, reportGeneralTypeIssues=false

from apps.kpl.models import Fixture, ExternalFixtureMapping
from apps.kpl.scrapers import detect_provider_from_url, scrape_lineups_for_url
from apps.kpl.services import upsert_fixture_lineup
from config.settings import base as settings
from util.selenium import selenium_session


logger = logging.getLogger(__name__)


@dataclass
class ParsedLineup:
    formation: Optional[str]
    is_confirmed: bool
    published_at: Optional[datetime]
    starters: List[Dict]
    bench: List[Dict]


PROVIDERS = [
    "sofascore",
    "flashscore",
    "liverpoolfc",
    "fkf",
    "club",
]


def build_lineup_url(provider: str, fixture: Fixture, *, side: str) -> Optional[str]:
    # Prefer explicit mapping per fixture/provider. Store full URL in provider_fixture_id.
    mapping = ExternalFixtureMapping.objects.filter(provider=provider, fixture=fixture).first()  # type: ignore[attr-defined]
    if mapping:
        value = mapping.provider_fixture_id
        if value.startswith("http://") or value.startswith("https://"):
            return value
        # Unknown format; skip
        return None
    if provider == "fkf":
        return None
    if provider == "club":
        return None
    if provider in {"sofascore", "flashscore"}:
        # Without explicit mapping we cannot reliably build URLs
        return None
    return None


def parse_lineup_from_source(driver, provider: str, url: str, *, side: str) -> Optional[ParsedLineup]:
    try:
        driver.get(url)
        # Allow URL-based detection so new sites can be plugged without code changes
        auto = detect_provider_from_url(url)
        selected = provider or auto or ""
        # Dispatch to provider-appropriate scraper via registry
        if selected:
            result = scrape_lineups_for_url(driver, url)
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
        return None
    except Exception as e:
        logger.warning("parse failed for %s: %s", provider, e)
        return None


def _with_backoff_attempts(max_attempts: int = 3):
    for attempt in range(1, max_attempts + 1):
        yield attempt, (2 ** attempt) + random.uniform(0, 1)


def fetch_lineup_for_fixture(fixture: Fixture) -> Tuple[bool, str]:
    if not settings.LINEUPS_SCRAPING_ENABLED:
        return False, "feature disabled"

    providers = [settings.PRIMARY_LINEUP_SOURCE] + [p for p in PROVIDERS if p != settings.PRIMARY_LINEUP_SOURCE]

    with selenium_session(
        command_executor=settings.SELENIUM_REMOTE_URL,
        headless=True,
        user_agent=settings.SCRAPER_USER_AGENT,
        page_load_timeout_seconds=30,
    ) as driver:
        for provider in providers:
            for side, team in [("home", fixture.home_team), ("away", fixture.away_team)]:
                url = build_lineup_url(provider, fixture, side=side)
                if not url:
                    continue
                for attempt, sleep_seconds in _with_backoff_attempts(3):
                    result = parse_lineup_from_source(driver, provider, url, side=side)
                    if result is None:
                        if attempt < 3:
                            with suppress(Exception):
                                import time
                                time.sleep(sleep_seconds)
                            continue
                        else:
                            break

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
                    logger.info("Lineup saved for fixture %s (%s/%s) via %s", fixture.id, team.name, side, provider)
                    break

    return True, "done"


@shared_task(autoretry_for=(Exception,), retry_backoff=30, retry_backoff_max=300, max_retries=5)
def fetch_lineup_for_fixture_task(fixture_id: str) -> str:
    fixture = Fixture.objects.filter(id=fixture_id).select_related("home_team", "away_team").first()  # type: ignore[attr-defined]
    if not fixture:
        return f"fixture {fixture_id} not found"
    ok, msg = fetch_lineup_for_fixture(fixture)
    return f"{ok}: {msg}"



@shared_task(autoretry_for=(Exception,), retry_backoff=30, retry_backoff_max=300, max_retries=3)
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
        Fixture.objects.filter(match_date__lte=window_end, match_date__gte=ko_grace_start)
        .select_related("home_team", "away_team")
        .prefetch_related("lineups")
        .order_by("match_date")
    )

    scheduled = 0
    max_concurrency = max(1, int(getattr(settings, "LINEUP_SCRAPER_MAX_CONCURRENCY", 2)))

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
        has_home_confirmed = any(l.side == "home" and l.is_confirmed for l in fixture.lineups.all())  # type: ignore[attr-defined]
        has_away_confirmed = any(l.side == "away" and l.is_confirmed for l in fixture.lineups.all())  # type: ignore[attr-defined]
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
                logger.warning("LINEUPS_ALERT_WEBHOOK configured; consider sending alert")
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

