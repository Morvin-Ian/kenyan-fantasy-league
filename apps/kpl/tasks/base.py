"""Shared Celery plumbing for the KPL scraping tasks.

Every sync task is built on :class:`ScrapingTask`, which fixes three things that
kept the old workers unstable:

1. **Overlap.** Beat fires on a schedule regardless of whether the previous run
   finished. Each task holds a Redis lock for its own name; a run that cannot
   take the lock exits immediately instead of piling a second scrape onto the
   same source.
2. **Retry policy.** Only :class:`SourceUnavailable` is retried, with
   exponential backoff and jitter. A :class:`ParseError` means the markup moved
   — retrying just re-downloads the same broken page, so it fails loudly instead.
3. **Wedged workers.** Hard and soft time limits stop a stalled scrape from
   holding a worker slot forever.
"""

from __future__ import annotations

import functools
import logging
from typing import Callable

from celery import Task, shared_task

from apps.kpl.scraping import SourceUnavailable
from apps.kpl.scraping.locks import LockNotAcquired, task_lock

logger = logging.getLogger(__name__)

# Long enough for the 306-row fixtures page plus per-host throttling, short
# enough that a hung run frees its worker slot within the beat interval.
SOFT_TIME_LIMIT = 8 * 60
TIME_LIMIT = 10 * 60


class ScrapingTask(Task):
    """Celery base class with retry and timeout defaults suited to scraping."""

    autoretry_for = (SourceUnavailable,)
    retry_backoff = 30
    retry_backoff_max = 10 * 60
    retry_jitter = True
    max_retries = 4

    # Redelivered if the worker dies mid-run, so a redeploy cannot lose a scrape.
    acks_late = True
    reject_on_worker_lost = True

    soft_time_limit = SOFT_TIME_LIMIT
    time_limit = TIME_LIMIT

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            "scraping task %s failed permanently: %s: %s",
            self.name,
            type(exc).__name__,
            exc,
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)


def scraping_task(*, name: str, lock: str | None = None, lock_ttl: int = 30 * 60, **options):
    """Register a locked, retrying scraping task.

    ``lock`` defaults to the task name. A run that finds the lock held returns
    ``{"skipped": "locked"}`` rather than raising, so a busy source shows up in
    the result backend as a skip rather than a stream of failures.
    """

    def decorator(func: Callable):
        lock_name = lock or name

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                with task_lock(lock_name, ttl=lock_ttl):
                    return func(*args, **kwargs)
            except LockNotAcquired:
                logger.warning(
                    "skipping %s: a previous run is still holding lock '%s'",
                    name,
                    lock_name,
                )
                return {"skipped": "locked", "task": name}

        return shared_task(base=ScrapingTask, name=name, **options)(wrapper)

    return decorator
