from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List


def _extract_formation(text: str) -> str | None:
    m = re.search(r"\b\d(?:-\d){2,}\b", text)
    return m.group(0) if m else None


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for s in items:
        key = s.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(s.strip())
    return out


def _collect_section(driver):
    # Flashscore usually has /lineups/ page with two blocks with player names
    containers = driver.find_elements(
        "xpath",
        "//div[contains(@class,'lineups')]//div[contains(@class,'lineup') or contains(@class,'team') or contains(@class,'players')]/ancestor::div[contains(@class,'lineups')] | //div[contains(@class,'lineups')]",
    )
    if containers:
        return containers[0]
    return None


def _collect_players_in_block(block) -> List[str]:
    names: List[str] = []
    # Player anchors or spans with name-like classes
    els = block.find_elements(
        "xpath",
        ".//a[contains(@href,'/player/')] | .//*[contains(translate(@class,'NAME','name'),'name') or contains(translate(@class,'PLAYER','player'),'player')]",
    )
    for el in els:
        t = el.text.strip()
        if 2 <= len(t) <= 40:
            names.append(t)
    return _dedupe_preserve_order(names)


def scrape_lineups(driver) -> Dict[str, Dict[str, Any]]:
    # Ensure we are on a /lineups/ page; caller should pass such URL
    root = _collect_section(driver)
    if not root:
        return {}

    # Identify two side blocks by density of player-like elements
    blocks = driver.find_elements(
        "xpath",
        ".//div[contains(@class,'lineup') or contains(@class,'team') or contains(@class,'players')]",
    )
    ranked = sorted(
        ((b, len(_collect_players_in_block(b))) for b in blocks),
        key=lambda x: x[1],
        reverse=True,
    )
    if len(ranked) < 2:
        return {}
    home_block, away_block = ranked[0][0], ranked[1][0]
    home_players = _collect_players_in_block(home_block)
    away_players = _collect_players_in_block(away_block)

    page_text = driver.page_source
    formation = _extract_formation(page_text) or None

    return {
        "home": {
            "formation": formation,
            "is_confirmed": True,
            "published_at": None,
            "starters": [{"name": n} for n in home_players[:11]],
            "bench": [{"name": n} for n in home_players[11:]],
        },
        "away": {
            "formation": formation,
            "is_confirmed": True,
            "published_at": None,
            "starters": [{"name": n} for n in away_players[:11]],
            "bench": [{"name": n} for n in away_players[11:]],
        },
    }
