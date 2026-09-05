"""Name normalisation shared by every provider.

Each source spells the same club differently — one writes "Mathare UTD" and
"Muranga SEAL" where another writes "Mathare United" and "Murang'a Seal FC".
Matching on the raw strings silently creates duplicate teams, so everything
funnels through :func:`team_key` before it touches the database.

Player names arrive from the primary source as ``"Joe Joseph IRUNGU WAITHIRA"``
— given names in title case, family names in caps. :func:`clean_player_name`
turns that into a consistent display name without losing the surname order.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Optional

# Words that carry no identity and only differ between sources.
_CLUB_NOISE = {
    "fc",
    "afc",
    "sc",
    "cf",
    "club",
    "football",
    "team",
    "squad",
}

# Expansions applied before noise removal, so "utd" and "united" collapse.
_WORD_ALIASES = {
    "utd": "united",
    "st": "saint",
    "hb": "homeboyz",
    "homeboys": "homeboyz",
}

# Cross-source spellings that normalisation alone cannot reconcile.
# Left-hand side is the normalised key, right-hand side the canonical key.
_TEAM_ALIASES = {
    "muranga seal": "murangaseal",
    "murangaseal": "murangaseal",
    "murangaaseal": "murangaseal",
    "bandari": "bandari",
    "bandarimtwara": "bandari",
    "kenyapolice": "police",
    "police": "police",
    "ulinzistars": "ulinzi",
    "ulinzi": "ulinzi",
    "apsbomet": "apsbomet",
    "bomet": "apsbomet",
    "nairobiunited": "nairobiunited",
    "mombasaunited": "mombasaunited",
    "migoriyouth": "migoriyouth",
    "3k": "3k",
    "kariobangisharks": "kariobangisharks",
    "ksharks": "kariobangisharks",
}


def strip_accents(value: str) -> str:
    return "".join(
        ch
        for ch in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(ch)
    )


def team_key(name: str) -> str:
    """Reduce a club name to a stable comparison key.

    ``"Mathare UTD"``, ``"Mathare United FC"`` and ``"mathare  united"`` all
    return ``"matharunited"``-style identical keys.
    """
    if not name:
        return ""

    value = strip_accents(name).lower()
    value = value.replace("&", " and ")
    # Drop anything that is not a letter, digit or space (apostrophes, dots,
    # hyphens) so "Murang'a" == "Muranga" and "F.C." == "FC".
    value = re.sub(r"[^a-z0-9\s]", " ", value)

    words = []
    for word in value.split():
        word = _WORD_ALIASES.get(word, word)
        if word in _CLUB_NOISE:
            continue
        words.append(word)

    key = "".join(words)
    return _TEAM_ALIASES.get(key, key)


def teams_match(left: str, right: str) -> bool:
    """True when two club names refer to the same club."""
    left_key, right_key = team_key(left), team_key(right)
    if not left_key or not right_key:
        return False
    if left_key == right_key:
        return True
    # One source occasionally carries an extra locality ("Bandari Mtwara").
    shorter, longer = sorted((left_key, right_key), key=len)
    return len(shorter) >= 5 and longer.startswith(shorter)


def clean_team_display_name(name: str) -> str:
    """Tidy a scraped club name for display without changing its identity."""
    value = re.sub(r"\s+", " ", (name or "").strip())
    value = re.sub(r"\bSquad\b$", "", value).strip()
    return value


def clean_player_name(name: str) -> Optional[str]:
    """Normalise a scraped player name, or return ``None`` if it is not a name.

    Strips minute markers (``"Elvis Noor 54'"``), collapses whitespace, and
    converts the source's ALL-CAPS surnames to title case while preserving word
    order. Placeholder rows such as ``",,,,,,, ............"`` return ``None``.
    """
    if not name:
        return None

    value = re.sub(r"\s*\(?\d{1,3}\s*'\s*\)?\s*$", "", name)
    value = re.sub(r"\s+", " ", value).strip(" .,-")

    if not value or not re.search(r"[A-Za-z]{2}", value):
        return None
    if re.fullmatch(r"\d+\s*'?", value):
        return None

    words = []
    for word in value.split():
        # Keep short all-caps tokens that are genuine initials ("J."), title-case
        # the shouted surnames.
        if word.isupper() and len(word) > 2:
            word = word.capitalize()
        elif word.islower():
            word = word.capitalize()
        words.append(word)
    return " ".join(words)


def player_key(name: str) -> str:
    """Comparison key for a player name: accent-free, punctuation-free, lower."""
    value = strip_accents(name or "").lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return " ".join(value.split())


def best_team_match(name: str, candidates: Iterable[str]) -> Optional[str]:
    """Return the candidate club name that matches ``name``, if any."""
    for candidate in candidates:
        if teams_match(name, candidate):
            return candidate
    return None
