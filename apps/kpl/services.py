from __future__ import annotations

import logging
import unicodedata
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple, cast

from django.db import transaction

from apps.kpl.models import (
    Fixture,
    FixtureLineup,
    FixtureLineupPlayer,
    Player,
    PlayerAlias,
    Team,
)


logger = logging.getLogger(__name__)


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join([c for c in normalized if not unicodedata.combining(c)])


def normalize_player_name(raw_name: str) -> str:
    if not raw_name:
        return ""
    name = _strip_accents(raw_name).lower().strip()
    for ch in ["\t", "\n", "\r", ",", ".", "'", "\"", "(", ")", "[", "]", "{", "}"]:
        name = name.replace(ch, " ")
    name = name.replace("-", " ")
    # Collapse multiple spaces
    name = " ".join(name.split())
    return name


def map_role_to_position(role: Optional[str], position_guess: Optional[str] = None) -> Optional[str]:
    tokens: List[str] = []
    if role:
        tokens.append(role.lower())
    if position_guess:
        tokens.append(position_guess.lower())
    token_str = " ".join(tokens)
    if any(k in token_str for k in ["gk", "keeper", "goalkeeper"]):
        return "GKP"
    if any(k in token_str for k in ["def", "full back", "centre back", "center back", "cb", "rb", "lb", "wing back", "back"]):
        return "DEF"
    if any(k in token_str for k in ["mid", "cm", "am", "dm", "winger", "wide", "number 10", "no 10", "playmaker"]):
        return "MID"
    if any(k in token_str for k in ["fwd", "fw", "striker", "forward", "cf", "attacker", "no 9", "number 9"]):
        return "FWD"
    return None


def _token_set_ratio(a: str, b: str) -> float:
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union


def match_player_for_team(
    *,
    team: Team,
    normalized_name: str,
    jersey_number: Optional[int],
) -> Optional[Player]:
    alias = cast(Optional[PlayerAlias], PlayerAlias.objects.filter(team=team, normalized_name=normalized_name).select_related("canonical_player").first())  # type: ignore[attr-defined]
    if alias:
        return alias.canonical_player

    team_players: List[Player] = list(cast(List[Player], list(Player.objects.filter(team=team))))  # type: ignore[attr-defined]

    # Exact normalized name match in Python
    for p in team_players:
        if normalize_player_name(p.name) == normalized_name:
            return p

    if jersey_number is not None:
        by_number = [p for p in team_players if p.jersey_number == jersey_number]
        if len(by_number) == 1:
            return by_number[0]

    # Fallback: simple token-set similarity
    best: Tuple[Optional[Player], float] = (None, 0.0)
    for p in team_players:
        sim = _token_set_ratio(normalize_player_name(p.name), normalized_name)
        if sim > best[1]:
            best = (p, sim)

    if best[0] is not None and best[1] >= 0.8:
        return best[0]

    logger.info(
        "No confident match for player name '%s' (team=%s, jersey=%s)",
        normalized_name,
        team.name,
        jersey_number,
    )
    return None


def upsert_fixture_lineup(
    *,
    fixture: Fixture,
    team: Team,
    side: str,
    source: str,
    formation: Optional[str],
    is_confirmed: bool,
    published_at: Optional[datetime],
    starters: Iterable[Dict],
    bench: Iterable[Dict],
) -> FixtureLineup:
    with transaction.atomic():
        lineup, _ = FixtureLineup.objects.select_for_update().get_or_create(  # type: ignore[attr-defined]
            fixture=fixture,
            team=team,
            side=side,
            defaults={
                "formation": formation,
                "is_confirmed": is_confirmed,
                "source": source,
                "published_at": published_at,
            },
        )

        changed = False
        if lineup.formation != formation:
            lineup.formation = formation
            changed = True
        if lineup.is_confirmed != is_confirmed:
            lineup.is_confirmed = is_confirmed
            changed = True
        if lineup.source != source:
            lineup.source = source
            changed = True
        if lineup.published_at != published_at:
            lineup.published_at = published_at
            changed = True
        if changed:
            lineup.save()

        # Replace players atomically
        lineup.players.all().delete()

        order_index = 1
        objects: List[FixtureLineupPlayer] = []

        def _build_player(entry: Dict, *, is_bench: bool, order_idx: int) -> FixtureLineupPlayer:
            raw_name = entry.get("name", "")
            normalized_name = normalize_player_name(raw_name)
            jersey_number = entry.get("jersey_number")
            role = entry.get("role")
            position_guess = entry.get("position_guess")
            position = map_role_to_position(role, position_guess)
            matched = match_player_for_team(
                team=team,
                normalized_name=normalized_name,
                jersey_number=jersey_number,
            )
            return FixtureLineupPlayer(
                lineup=lineup,
                player=matched,
                position=position,
                order_index=order_idx,
                is_bench=is_bench,
            )

        for item in starters:
            objects.append(_build_player(item, is_bench=False, order_idx=order_index))
            order_index += 1

        for item in bench:
            objects.append(_build_player(item, is_bench=True, order_idx=order_index))
            order_index += 1

        if objects:
            FixtureLineupPlayer.objects.bulk_create(objects, batch_size=64)  # type: ignore[attr-defined]

    return lineup


