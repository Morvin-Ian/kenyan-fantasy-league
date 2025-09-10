from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse


PROVIDER_DOMAINS = {
    "sofascore": ["sofascore.com"],
    "flashscore": ["flashscore.com", "flashscore.co.ke"],
    # Add more providers here
    "kenyafootballdata": ["kenyafootballdata.com"],
}


def detect_provider_from_url(url: str) -> Optional[str]:
    host = urlparse(url).netloc.lower()
    for provider, domains in PROVIDER_DOMAINS.items():
        for domain in domains:
            if domain in host:
                return provider
    return None


def scrape_lineups_for_url(driver, url: str):
    provider = detect_provider_from_url(url)
    if provider == "sofascore":
        from .sofascore import scrape_lineups  # type: ignore

        return scrape_lineups(driver)
    if provider == "flashscore":
        from .flashscore import scrape_lineups  # type: ignore

        return scrape_lineups(driver)
    
    if provider == "kenyafootballdata":
        from .kenyafootballdata import scrape_lineups  # type: ignore

        return scrape_lineups(driver)
    return {}


