"""Shared test configuration.

The default cache is Redis (``config.settings.base.CACHES``), and the scraping
layer leans on it: ``task_lock`` takes its lock there, ``current_season`` caches
the discovered season, and conditional GETs store ETags there. CI runs no Redis
service, so every one of those tests died with

    redis.exceptions.ConnectionError: Error -3 connecting to redis:6379

Tests should not need a running Redis to exercise that logic, so the whole suite
runs against local memory instead.
"""

import pytest
from django.core.cache import cache

LOCMEM_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "kpl-tests",
    }
}


@pytest.fixture(autouse=True)
def local_memory_cache(settings):
    """Swap Redis for local memory, and start every test with it empty.

    Clearing matters: a locmem cache is keyed by LOCATION in a process-global
    dict, so a lock left behind by one test would still be held in the next.
    """
    settings.CACHES = LOCMEM_CACHE
    cache.clear()
    yield
    cache.clear()
