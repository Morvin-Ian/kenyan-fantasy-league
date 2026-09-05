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

    Raises:
        LockNotAcquired: if the lock is already held elsewhere.
    """
    key = f"kpl:scrape:lock:{name}"
    token = uuid.uuid4().hex

    # cache.add is atomic (Redis SETNX), so only one worker wins the race.
    if not cache.add(key, token, timeout=ttl):
        raise LockNotAcquired(f"lock '{name}' is already held")

    logger.debug("acquired lock %s (ttl=%ss)", name, ttl)
    try:
        yield
    finally:
        # Only release a lock we still own; if the TTL expired and someone else
        # took over, deleting the key would drop their lock.
        if cache.get(key) == token:
            cache.delete(key)
            logger.debug("released lock %s", name)
        else:
            logger.warning("lock %s expired before the task finished", name)
