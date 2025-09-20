from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List


def _parse_datetime(text: str | None) -> datetime | None:
    return None


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


def _collect_player_names(container) -> List[str]:
    names: List[str] = []
    # Prefer true player links
    anchors = container.find_elements("xpath", ".//a[contains(@href, '/player/')]")
    for a in anchors:
        t = a.text.strip()
        if 2 <= len(t) <= 40:
            names.append(t)
    if names:
        return _dedupe_preserve_order(names)
    # Fallback: elements that look like player/name entries
    elems = container.find_elements(
        "xpath",
        ".//*[contains(translate(@class,'NAME','name'),'name') or contains(translate(@class,'PLAYER','player'),'player')][string-length(normalize-space(text()))>0]",
    )
    for el in elems:
        t = el.text.strip()
        if 2 <= len(t) <= 40:
            names.append(t)
    return _dedupe_preserve_order(names)


def scrape_lineups(driver) -> Dict[str, Dict[str, Any]]:
    # Activate Lineups tab if present
    try:
        tab = driver.find_element(
            "xpath",
            "//a[contains(@href, '#tab:lineups')] | //button[normalize-space()='Lineups']",
        )
        tab.click()
    except Exception:
        pass

    # Locate the lineups panel
    containers = driver.find_elements(
        "xpath",
        "//div[contains(@class,'lineup') or contains(@class,'Lineup') or .//text()[contains(., 'Formation')]] | //section[.//text()[contains(., 'Formation')]]",
    )
    if not containers:
        return {}

    # Try to identify two sides: use first two containers that contain many player-like elements
    side_blocks = []
    for c in containers:
        players = _collect_player_names(c)
        if len(players) >= 8:  # likely a side block
            side_blocks.append((c, players))
    if len(side_blocks) < 2:
        # fallback: use the two largest containers by player-like count
        ranked = sorted(((c, _collect_player_names(c)) for c in containers), key=lambda x: len(x[1]), reverse=True)
        side_blocks = ranked[:2]
    if len(side_blocks) < 2:
        return {}

    # Extract formation from text if available
    page_text = driver.page_source
    formation = _extract_formation(page_text) or None

    result: Dict[str, Dict[str, Any]] = {
        "home": {
            "formation": formation,
            "is_confirmed": True,
            "published_at": None,
            "starters": [],
            "bench": [],
        },
        "away": {
            "formation": formation,
            "is_confirmed": True,
            "published_at": None,
            "starters": [],
            "bench": [],
        },
    }

    # Assign starters/bench by heuristic: first 11 are starters; rest (if any) bench
    home_players = side_blocks[0][1]
    away_players = side_blocks[1][1]
    result["home"]["starters"] = [{"name": n} for n in home_players[:11]]
    result["home"]["bench"] = [{"name": n} for n in home_players[11:]]
    result["away"]["starters"] = [{"name": n} for n in away_players[:11]]
    result["away"]["bench"] = [{"name": n} for n in away_players[11:]]

    return result


