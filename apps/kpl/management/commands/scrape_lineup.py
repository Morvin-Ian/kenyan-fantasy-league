from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.kpl.models import Fixture
from apps.kpl.tasks.lineups import fetch_lineup_for_fixture


class Command(BaseCommand):
    help = "Scrape lineup for a single fixture using mapped provider URL(s) and persist results"

    def add_arguments(self, parser):
        parser.add_argument("fixture_id", type=str, help="Fixture UUID to scrape")

    def handle(self, *args, **options):
        fixture_id = options["fixture_id"]
        fixture = Fixture.objects.filter(id=fixture_id).select_related("home_team", "away_team").first()  # type: ignore[attr-defined]
        if not fixture:
            raise CommandError(f"Fixture {fixture_id} not found")
        ok, msg = fetch_lineup_for_fixture(fixture)
        if not ok:
            self.stderr.write(self.style.WARNING(f"Scrape finished with status={ok} message={msg}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Scrape succeeded: {msg}"))
