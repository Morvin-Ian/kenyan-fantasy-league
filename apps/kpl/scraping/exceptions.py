"""Exception hierarchy for the KPL scraping layer.

The split matters for retry policy: ``SourceUnavailable`` is transient and worth
retrying, ``ParseError``/``StructureChanged`` mean the source markup moved and a
retry would only burn the same request again.
"""

from __future__ import annotations


class ScrapeError(Exception):
    """Base class for every failure raised by the scraping layer."""


class SourceUnavailable(ScrapeError):
    """The remote host could not be reached, timed out, or returned 5xx/429.

    Transient. Celery tasks retry these with exponential backoff.
    """


class ParseError(ScrapeError):
    """The page was fetched but could not be parsed into the expected shape."""


class StructureChanged(ParseError):
    """A structural assumption (table/column/row count) no longer holds.

    Raised instead of silently writing empty or partial data, so a source
    redesign shows up as a loud failure rather than a wiped table.
    """


class SeasonNotFound(ScrapeError):
    """No current season could be discovered for the configured competition."""
