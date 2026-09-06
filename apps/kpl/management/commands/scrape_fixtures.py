"""Run the live-score update from the command line.

    python manage.py scrape_fixtures

Useful for checking the live source by hand — that the browser renders, that the
competition filter matches, and that the rows resolve onto fixtures — without
waiting for the schedule.

This used to drive the per-fixture browser monitor in ``tasks/live_games.py``.
That polled one match at a time from its own Celery periodic task; a single task
now reads every match on the page in one pass, so there is nothing to point at a
particular fixture or date any more.
"""

import json

from django.core.management.base import BaseCommand

from apps.kpl.tasks.live import sync_live_scores


class Command(BaseCommand):
    help = "Update in-play and just-finished fixtures from the live source."

    def handle(self, *args, **options):
        self.stdout.write("→ reading the live scores page ...")

        # .run() executes in-process rather than dispatching to a worker.
        result = sync_live_scores.run()

        if result.get("success") is False:
            self.stdout.write(self.style.ERROR(f"  failed: {result.get('error')}"))
            return

        self.stdout.write(self.style.SUCCESS(f"  {json.dumps(result, default=str)}"))
