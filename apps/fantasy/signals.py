"""Cache invalidation for the Fantasy app.

Every receiver here goes through :func:`drop`, which swallows its own failures.
Cache housekeeping is not allowed to break a write: these previously called
``get_redis_connection()`` directly and unguarded, so a Redis outage turned
every team save, selection change and points update into a hard error, and the
whole suite failed against any cache backend that is not Redis.
"""

import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.fantasy.models import FantasyPlayer, FantasyTeam, TeamSelection
from apps.kpl.models import FixtureLineup, Gameweek, TopcorerData

logger = logging.getLogger(__name__)


def drop(*keys: str) -> None:
    """Delete cache keys, treating a wildcard as a pattern. Never raises.

    Pattern deletion needs the Redis client; where that is unavailable (local
    memory in tests, or Redis being down) the pattern is skipped rather than
    allowed to propagate.
    """
    for key in keys:
        try:
            if "*" in key:
                try:
                    from django_redis import get_redis_connection

                    connection = get_redis_connection("default")
                except (ImportError, NotImplementedError, AttributeError):
                    continue
                matched = connection.keys(key)
                if matched:
                    connection.delete(*matched)
            else:
                cache.delete(key)
        except Exception as exc:  # noqa: BLE001 - housekeeping must not break writes
            logger.warning("could not invalidate cache key %r: %s", key, exc)


@receiver([post_save, post_delete], sender=TeamSelection)
def invalidate_team_selection_cache(sender, instance, **kwargs):
    """Invalidate caches when team selection is created/updated/deleted."""
    drop(
        f"gameweek_selection_{instance.fantasy_team_id}_{instance.gameweek_id}",
        f"available_gameweeks_{instance.fantasy_team_id}",
        f"user_team_{instance.fantasy_team.user_id}_*",
    )


@receiver(post_save, sender=Gameweek)
def invalidate_gameweek_cache(sender, instance, **kwargs):
    """Invalidate active gameweek cache when gameweek is updated."""
    if instance.is_active:
        drop("active_gameweek_number", "available_gameweeks_*")


@receiver([post_save, post_delete], sender=FixtureLineup)
def invalidate_lineup_cache(sender, instance, **kwargs):
    """Invalidate fixture lineup cache when lineup is updated."""
    drop(f"fixture_lineups_{instance.fixture_id}")


@receiver([post_save, post_delete], sender=TopcorerData)
def invalidate_leaderboard_cache(sender, instance, **kwargs):
    """Invalidate goals leaderboard cache when topscorer data is updated."""
    drop("goals_leaderboard_limit_*")


@receiver([post_save, post_delete], sender=FantasyPlayer)
def invalidate_fantasy_player_cache(sender, instance, **kwargs):
    """Invalidate team players cache when fantasy player is updated."""
    drop(
        f"team_players_{instance.fantasy_team_id}",
        f"user_team_{instance.fantasy_team.user_id}_*",
    )


@receiver([post_save, post_delete], sender=FantasyTeam)
def invalidate_fantasy_team_cache(sender, instance, **kwargs):
    """Invalidate fantasy team cache when team is updated."""
    drop(f"user_team_{instance.user_id}_*")
