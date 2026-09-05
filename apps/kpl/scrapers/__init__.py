"""Lineup scraper dispatch.

Which hostname belongs to which provider comes from ``SCRAPER_PROVIDER_HOSTS``,
so the repository does not record the sites this project reads. Format is a
comma-separated list of ``provider=host`` pairs::

    SCRAPER_PROVIDER_HOSTS=primary=a.example
"""

from __future__ import annotations

from typing import Dict, List, Optional
from urllib.parse import urlparse

from django.conf import settings


def provider_domains() -> Dict[str, List[str]]:
    hosts: Dict[str, List[str]] = {}
    for chunk in getattr(settings, "SCRAPER_PROVIDER_HOSTS", "").split(","):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        provider, _, host = chunk.partition("=")
        hosts.setdefault(provider.strip(), []).append(host.strip().lower())
    return hosts


def detect_provider_from_url(url: str) -> Optional[str]:
    host = urlparse(url).netloc.lower()
    for provider, domains in provider_domains().items():
        if any(domain and domain in host for domain in domains):
            return provider
    return None


def scrape_lineups_for_url(driver, url: str):
    """Return ``{"home": {...}, "away": {...}}`` for a match page, or ``{}``.

    ``driver`` is accepted for call-site compatibility and unused: the only
    remaining adapter reads static HTML over plain HTTP.
    """
    if detect_provider_from_url(url) == "primary":
        from .primary import scrape_lineups

        return scrape_lineups(url)
    return {}
