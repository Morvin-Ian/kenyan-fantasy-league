"""Drop cached read endpoints.

    python manage.py clear_cache            # every cached read endpoint
    python manage.py clear_cache --list     # what would be dropped
    python manage.py clear_cache players    # just the player lists

Needed once on the deploy that fixes the invalidation: the player list caches
under ``players_list_team_{team}_page_{n}`` for four hours, and the signal that
was meant to clear it dropped ``players_active_list_*`` — a key nothing writes.
Anything cached before that fix survives until it expires on its own, so the API
keeps serving squads in which every player is a midfielder.

Safe at any time: these are all read-through caches, so the next request
repopulates them from the database.
"""

from __future__ import annotations

from django.core.cache import cache
from django.core.management.base import BaseCommand

# What the read endpoints write, by the name you would ask for it under.
GROUPS = {
    "players": ("players_list_team_*", "team_players_*"),
    "standings": ("standings_list_page_*",),
    "lineups": ("fixture_lineups_*",),
    "gameweeks": ("active_gameweek_number", "available_gameweeks_*"),
    "leaderboard": ("goals_leaderboard_limit_*",),
    "teams": ("user_team_*",),
}


class Command(BaseCommand):
    help = "Drop cached read endpoints so the next request rebuilds them."

    def add_arguments(self, parser):
        parser.add_argument(
            "groups",
            nargs="*",
            choices=sorted(GROUPS) + [[]],
            help="Which caches to drop. Default: all of them.",
        )
        parser.add_argument(
            "--list", action="store_true", help="Show the patterns and exit."
        )

    def handle(self, *args, **options):
        chosen = options["groups"] or sorted(GROUPS)

        if options["list"]:
            for name in chosen:
                self.stdout.write(f"  {name}: {', '.join(GROUPS[name])}")
            return

        delete_pattern = getattr(cache, "delete_pattern", None)
        dropped = 0

        for name in chosen:
            for pattern in GROUPS[name]:
                try:
                    if pattern.endswith("*"):
                        if delete_pattern is None:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  {pattern}: backend cannot delete by pattern"
                                )
                            )
                            continue
                        count = delete_pattern(pattern)
                        dropped += count or 0
                        self.stdout.write(f"  {pattern}: {count or 0} key(s)")
                    else:
                        cache.delete(pattern)
                        dropped += 1
                        self.stdout.write(f"  {pattern}: dropped")
                except Exception as exc:  # noqa: BLE001 - report and carry on
                    self.stdout.write(
                        self.style.ERROR(f"  {pattern}: {type(exc).__name__}: {exc}")
                    )

        self.stdout.write(self.style.SUCCESS(f"Dropped {dropped} cache key(s)."))
