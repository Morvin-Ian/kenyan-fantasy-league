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

from apps.kpl.models import (
    FixtureLineup,
    Gameweek,
    Player,
    Standing,
    Team,
    TopcorerData,
)

logger = logging.getLogger(__name__)


def drop(*keys: str) -> None:
    """Delete cache keys, treating one ending in ``*`` as a pattern.

    Never raises: a failed invalidation costs a stale read, while letting the
    exception out would fail the save that triggered it.
    """
    for key in keys:
        try:
            if key.endswith("*"):
                delete_pattern = getattr(cache, "delete_pattern", None)
                if delete_pattern is None:
                    # Backends without pattern deletion (locmem, in tests) have
                    # nothing to invalidate that anyone is reading.
                    logger.debug("cache backend cannot delete by pattern: %s", key)
                    continue
                delete_pattern(key)
            else:
                cache.delete(key)
        except Exception as exc:  # noqa: BLE001 - must not break the write
            logger.warning("could not invalidate cache key %r: %s", key, exc)


@receiver([post_save, post_delete], sender=Player)
def invalidate_player_cache(sender, instance, **kwargs):
    """Drop the cached player lists.

    This dropped ``players_active_list_*`` — a key nothing has ever written. The
    endpoint caches under ``players_list_team_{team}_page_{n}``
    (``apps/kpl/views.py``) for four hours, so the list was never invalidated at
    all: after sync_players filled in real positions the API kept serving a
    squad in which everyone was still a midfielder, and picking a team could
    only fill the midfield.
    """
    drop("players_list_team_*", "team_players_*")


@receiver([post_save, post_delete], sender=Team)
def invalidate_team_cache(sender, instance, **kwargs):
    """Drop anything that embeds a club.

    The player payloads carry their club's name and jersey, so a new jersey or
    badge has to invalidate the player lists too — there was no Team receiver at
    all, so those changes were invisible until the four-hour entry expired.
    """
    drop("players_list_team_*", "team_players_*", "standings_list_page_*")


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
