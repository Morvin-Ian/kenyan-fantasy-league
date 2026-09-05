"""Redis-backed advisory locks for scraping tasks.

Beat fires on a fixed schedule; a slow scrape must not be joined by the next
one. Every sync task takes a named lock, and a run that cannot get the lock
exits cleanly instead of queueing up behind the running one and multiplying load
on the source.

The lock always carries a TTL, so a worker killed mid-scrape (OOM, redeploy)
cannot leave the task permanently locked out.
"""

from __future__ import annotations

import logging
import uuid
from contextlib import contextmanager

from django.core.cache import cache

logger = logging.getLogger(__name__)

DEFAULT_LOCK_TTL = 30 * 60


class LockNotAcquired(RuntimeError):
    """Another worker already holds this lock."""


@contextmanager
def task_lock(name: str, ttl: int = DEFAULT_LOCK_TTL):
    """Hold an exclusive lock named ``name`` for the duration of the block.

    If the cache backend is unreachable the block still runs, unlocked, with a
    warning. Overlapping scrapes are recoverable — every sync is idempotent —
    whereas refusing to run would turn a brief Redis blip into a total stop on
    data collection.

    Raises:
        LockNotAcquired: if the lock is genuinely held by someone else.
    """
    key = f"kpl:scrape:lock:{name}"
    token = uuid.uuid4().hex

    try:
        # cache.add is atomic (Redis SETNX), so only one worker wins the race.
        acquired = cache.add(key, token, timeout=ttl)
    except Exception as exc:  # noqa: BLE001 - backend down, not a lock conflict
        logger.warning("cache unavailable (%s); running '%s' without a lock", exc, name)
        yield
        return

    if not acquired:
        raise LockNotAcquired(f"lock '{name}' is already held")

    logger.debug("acquired lock %s (ttl=%ss)", name, ttl)
    try:
        yield
    finally:
        try:
            # Only release a lock we still own; if the TTL expired and someone
            # else took over, deleting the key would drop their lock.
            if cache.get(key) == token:
                cache.delete(key)
                logger.debug("released lock %s", name)
            else:
                logger.warning("lock %s expired before the task finished", name)
        except Exception as exc:  # noqa: BLE001 - the work is already done
            logger.warning("could not release lock %s: %s", name, exc)
