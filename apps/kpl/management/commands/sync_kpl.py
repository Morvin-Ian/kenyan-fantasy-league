"""Run the KPL scrapers from the command line.

Useful for the first import on a fresh database, for backfilling after a source
outage, and for checking a source by hand before trusting the schedule::

    python manage.py sync_kpl                     # full pipeline, in order
    python manage.py sync_kpl --step teams --step fixtures
    python manage.py sync_kpl --list              # what is available
    python manage.py sync_kpl --season            # just report the season found
"""

from __future__ import annotations

import json
import time

from django.core.management.base import BaseCommand, CommandError

from apps.kpl.tasks import sync

# Declaration order is dependency order: clubs must exist before anything can
# resolve against them, and the calendar before results hang off it.
STEPS = {
    "teams": sync.sync_teams,
    "logos": sync.sync_team_logos,
    "fixtures": sync.sync_fixtures,
    "players": sync.sync_players,
    "results": sync.sync_results,
    "standings": sync.sync_standings,
    "scorers": sync.sync_top_scorers,
    "match-details": sync.sync_match_details,
}

# Everything the nightly pipeline runs; "match-details" is opt-in.
DEFAULT_STEPS = ["teams", "logos", "fixtures", "players", "results", "standings", "scorers"]


class Command(BaseCommand):
    help = "Scrape Kenyan Premier League data into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--step",
            action="append",
            dest="steps",
            choices=sorted(STEPS),
            help="Run only this step. Repeatable; runs in the order given.",
        )
        parser.add_argument(
            "--list", action="store_true", help="List the available steps and exit."
        )
        parser.add_argument(
            "--season",
            action="store_true",
            help="Report the season the scraper discovered and exit.",
        )
        parser.add_argument(
            "--refresh-season",
            action="store_true",
            help="Bypass the cached season id and rediscover it first.",
        )

    def handle(self, *args, **options):
        if options["list"]:
            for name in STEPS:
                self.stdout.write(f"  {name}")
            return

        if options["refresh_season"] or options["season"]:
            season = sync.current_season(refresh=True)
            self.stdout.write(
                self.style.SUCCESS(f"season: {season.label} ({season.tournament_id})")
            )
            if options["season"]:
                return

        steps = options["steps"] or DEFAULT_STEPS
        failures = 0

        for name in steps:
            task = STEPS.get(name)
            if task is None:
                raise CommandError(f"unknown step {name!r}")

            self.stdout.write(f"→ {name} ...")
            started = time.monotonic()
            try:
                # .run() executes in-process rather than dispatching to a worker,
                # which is what you want from a shell.
                result = task.run()
            except Exception as exc:  # noqa: BLE001 - report and carry on
                failures += 1
                self.stderr.write(
                    self.style.ERROR(f"  {name} failed: {type(exc).__name__}: {exc}")
                )
                continue

            elapsed = time.monotonic() - started
            self.stdout.write(
                self.style.SUCCESS(f"  {name} ok in {elapsed:.1f}s: {json.dumps(result, default=str)}")
            )

        if failures:
            raise CommandError(f"{failures} of {len(steps)} steps failed")
        self.stdout.write(self.style.SUCCESS("done"))
