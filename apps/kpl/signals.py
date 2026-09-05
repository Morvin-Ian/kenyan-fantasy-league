"""Cache invalidation for the read endpoints.

These fire on ordinary model saves, including the bulk ones the sync tasks do —
``sync_players`` alone writes over a thousand rows. They used to reach for
``django_redis.get_redis_connection`` directly, which made every one of those
saves depend on Redis being up: a single blip would raise mid-sync and abort the
run. Cache invalidation is housekeeping, so it now goes through Django's cache
API and never propagates a backend failure.

Going through the cache API also means the app is no longer pinned to Redis;
any backend works, which is what lets the test suite run without one.
"""

import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.kpl.models import FixtureLineup, Gameweek, Player, Standing, TopcorerData

logger = logging.getLogger(__name__)


def drop(key: str) -> None:
    """Delete a cache key, or every key matching it when it ends in ``*``.

    Never raises: a failed invalidation costs a stale read, while letting the
    exception out would fail the save that triggered it.
    """
    try:
        if key.endswith("*"):
            delete_pattern = getattr(cache, "delete_pattern", None)
            if delete_pattern is None:
                # Backends without pattern deletion (locmem, in tests) have
                # nothing to invalidate that anyone is reading.
                logger.debug("cache backend cannot delete by pattern: %s", key)
                return
            delete_pattern(key)
        else:
            cache.delete(key)
    except Exception as exc:  # noqa: BLE001 - housekeeping must not break writes
        logger.warning("could not invalidate cache key %r: %s", key, exc)


@receiver([post_save, post_delete], sender=Player)
def invalidate_player_cache(sender, instance, **kwargs):
    drop("players_active_list_*")


@receiver([post_save, post_delete], sender=Standing)
def invalidate_standing_cache(sender, instance, **kwargs):
    drop("standings_list_page_*")


@receiver([post_save, post_delete], sender=FixtureLineup)
def invalidate_fixture_lineup_cache(sender, instance, **kwargs):
    drop(f"fixture_lineups_{instance.fixture_id}")


@receiver([post_save, post_delete], sender=TopcorerData)
def invalidate_topscorer_cache(sender, instance, **kwargs):
    drop("goals_leaderboard_limit_*")


@receiver(post_save, sender=Gameweek)
def invalidate_gameweek_cache_on_active_change(sender, instance, **kwargs):
    if instance.is_active:
        drop("active_gameweek_number")
