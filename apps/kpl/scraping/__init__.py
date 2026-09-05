"""Scraping layer for external Kenyan Premier League data sources.

``providers`` holds one module per source; everything above it deals in the
dataclasses those modules return, never in HTML.
"""

from .exceptions import (
    ParseError,
    ScrapeError,
    SeasonNotFound,
    SourceUnavailable,
    StructureChanged,
)
from .locks import LockNotAcquired, task_lock

__all__ = [
    "ScrapeError",
    "SourceUnavailable",
    "ParseError",
    "StructureChanged",
    "SeasonNotFound",
    "task_lock",
    "LockNotAcquired",
]
