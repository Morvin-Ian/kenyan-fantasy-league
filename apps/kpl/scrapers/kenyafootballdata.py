from __future__ import annotations

from typing import Any, Dict, List
from selenium.webdriver.common.by import By


def _text_to_names(text: str) -> List[str]:
    # Split lines and commas, clean whitespace
    parts = []
    for line in text.splitlines():
        for chunk in line.split(','):
            name = chunk.strip()
            if name:
                parts.append(name)
    return parts


def scrape_lineups(driver) -> Dict[str, Dict[str, Any]]:
    # KenyaFootballData pages include a visible Lineups section with a 3-column table (#, home, away)
    home: List[str] = []
    away: List[str] = []

    # Try a sequence of robust XPaths to locate the lineups rows
    xpaths = [
        "//h2[contains(normalize-space(.), 'Lineups')]/following::table[1]//tr",
        "//h3[contains(normalize-space(.), 'Lineups')]/following::table[1]//tr",
        "//table[.//th[contains(., '#')]][.//tr]/tbody/tr | //table[.//th[contains(., '#')]][.//tr]/tr",
        "//div[contains(., 'Lineups')]//table//tr",
    ]

    rows: List[Any] = []
    for xp in xpaths:
        try:
            rows = driver.find_elements(By.XPATH, xp)
        except Exception:
            rows = []
        if rows and len(rows) >= 5:  # likely a lineup table
            break

    if rows:
        for r in rows:
            cells = r.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 3:
                # Prefer anchor text inside cells
                def cell_text(cell):
                    links = cell.find_elements(By.TAG_NAME, 'a')
                    if links:
                        return links[0].text.strip()
                    return cell.text.strip()

                home_text = cell_text(cells[1])
                away_text = cell_text(cells[2])
                if home_text:
                    home.append(home_text)
                if away_text:
                    away.append(away_text)
    else:
        # Fallback: naive parse using page_source for markdown-like tables
        page = driver.page_source
        lines = [l.strip() for l in page.splitlines() if l.strip().startswith('|')]
        for l in lines:
            cols = [c.strip() for c in l.split('|') if c.strip()]
            # Expect something like: | 1. | Home Name | Away Name |
            if len(cols) >= 3 and any(ch.isdigit() for ch in cols[0][:3]):
                home.append(cols[1])
                away.append(cols[2])

    # Normalize collected names
    home_list = []
    away_list = []
    for h in home:
        home_list.extend([{"name": n} for n in _text_to_names(h)])
    for a in away:
        away_list.extend([{"name": n} for n in _text_to_names(a)])

    return {
        "home": {"formation": None, "is_confirmed": True, "published_at": None, "starters": home_list[:11], "bench": home_list[11:]},
        "away": {"formation": None, "is_confirmed": True, "published_at": None, "starters": away_list[:11], "bench": away_list[11:]},
    }


