"""Recompute stored gameweek scores from the recorded performances.

    python manage.py rescore --dry-run     # report what would change
    python manage.py rescore               # every gameweek with a selection
    python manage.py rescore --gameweek 7  # just one

Points used to be added onto ``FantasyTeam.total_points`` as match events
arrived. They are now derived: the scoring engine writes a score per gameweek
onto ``TeamSelection.points``, and a team's season total is the sum of those.

That makes this command necessary once, on the deploy that introduces it.
Existing selections carry the column's default of 0, so until they are scored a
team's derived total would be lower than the total it accumulated under the old
scheme — and the first match event to touch that team would write the lower
number. Running this immediately after migrating closes that window.

It is safe to re-run at any time: nothing is accumulated, every score is
recomputed from ``PlayerPerformance``, which this command never writes to.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.fantasy.models import FantasyTeam, TeamSelection
from apps.fantasy.services import scoring_engine
from apps.kpl.models import Gameweek


class Command(BaseCommand):
    help = "Recompute gameweek scores and season totals from player performances."

    def add_arguments(self, parser):
        parser.add_argument(
            "--gameweek",
            type=int,
            default=None,
            help="Only this gameweek number. Default: every one with a selection.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing anything.",
        )

    def handle(self, *args, **options):
        number = options["gameweek"]
        dry_run = options["dry_run"]

        gameweeks = (
            Gameweek.objects.filter(team_selections__is_finalized=True)
            .distinct()
            .order_by("number")
        )
        if number is not None:
            gameweeks = gameweeks.filter(number=number)
            if not gameweeks.exists():
                raise CommandError(
                    f"no finalised team selections for gameweek {number}"
                )

        if not gameweeks.exists():
            self.stdout.write("No finalised team selections; nothing to score.")
            return

        before = {team.pkid: team.total_points for team in FantasyTeam.objects.all()}

        for gameweek in gameweeks:
            selections = TeamSelection.objects.filter(
                gameweek=gameweek, is_finalized=True
            ).select_related("fantasy_team", "captain", "vice_captain", "gameweek")

            if dry_run:
                changed = 0
                for selection in selections:
                    result = scoring_engine.calculate_selection(selection)
                    if result.points != selection.points:
                        changed += 1
                        self.stdout.write(
                            f"  GW{gameweek.number} {selection.fantasy_team.name}: "
                            f"{selection.points} -> {result.points}"
                        )
                self.stdout.write(
                    f"GW{gameweek.number}: {changed} of {selections.count()} would change"
                )
                continue

            scored = scoring_engine.recalculate_gameweek(gameweek)
            self.stdout.write(
                self.style.SUCCESS(f"GW{gameweek.number}: scored {scored} team(s)")
            )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run: nothing was written."))
            return

        moved = []
        for team in FantasyTeam.objects.all().order_by("-total_points"):
            was = before.get(team.pkid, 0)
            if was != team.total_points:
                moved.append((team.name, was, team.total_points))

        if moved:
            self.stdout.write("\nSeason totals that changed:")
            for name, was, now in moved:
                self.stdout.write(f"  {name}: {was} -> {now}")
        self.stdout.write(self.style.SUCCESS(f"\nDone. {len(moved)} total(s) changed."))
