"""Turn a finalised team selection into a gameweek score.

This replaces the old approach, where each match event added points straight
onto ``FantasyTeam.total_points``. That was wrong in several ways at once:

* it accumulated, so re-running a fixture double counted and a corrected stat
  could never be taken back off;
* the captain's points were never actually doubled — the code set a ``role``
  label and then added the undoubled total;
* chips were honoured in the serializer but not in the stored total, so a
  Triple Captain week displayed 3x and banked 2x, and Bench Boost displayed
  bench points and banked none;
* a starter who did not play simply lost their points, because there was no
  automatic substitution.

Everything here is recomputed from the selection and the performances, so it is
idempotent: running it again on the same data produces the same number, and
running it after a correction produces the corrected number.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from django.db import transaction
from django.utils import timezone

from apps.fantasy import scoring
from apps.fantasy.models import (
    ChipType,
    FantasyPlayer,
    FantasyTeam,
    PlayerPerformance,
    TeamSelection,
)

logger = logging.getLogger(__name__)

# The shape a valid eleven has to keep while substitutes are brought on.
MIN_BY_POSITION = {"GKP": 1, "DEF": 3, "MID": 0, "FWD": 1}
MAX_BY_POSITION = {"GKP": 1, "DEF": 5, "MID": 5, "FWD": 3}


@dataclass
class Substitution:
    off: FantasyPlayer
    on: FantasyPlayer


@dataclass
class SelectionResult:
    points: int
    gross_points: int
    transfer_hit: int
    substitutions: List[Substitution]
    captain: Optional[FantasyPlayer]
    captain_multiplier: int
    counted: Dict[object, int]

    @property
    def auto_subs_made(self) -> int:
        return len(self.substitutions)


def _played(performance: Optional[PlayerPerformance]) -> bool:
    return bool(performance and performance.minutes_played > 0)


def _position(fantasy_player: FantasyPlayer) -> str:
    position = fantasy_player.player.position
    return position if position in MAX_BY_POSITION else "MID"


def _formation_is_legal(positions: List[str]) -> bool:
    counts = {key: 0 for key in MAX_BY_POSITION}
    for position in positions:
        counts[position] += 1
    if sum(counts.values()) != 11:
        return False
    return all(
        MIN_BY_POSITION[key] <= counts[key] <= MAX_BY_POSITION[key] for key in counts
    )


def auto_substitute(
    starters: List[FantasyPlayer],
    bench: List[FantasyPlayer],
    performances: Dict[object, PlayerPerformance],
) -> Tuple[List[FantasyPlayer], List[Substitution]]:
    """Replace starters who did not play with bench players who did.

    Bench players are tried in ``bench_order``, and a substitution is only made
    when the eleven that results is still a legal formation — so a defender is
    not brought on if that would leave the side with two at the back, and the
    reserve keeper only ever replaces the keeper.

    Returns the final eleven and the substitutions that were made.
    """
    final = list(starters)
    used: List[Substitution] = []

    non_players = [p for p in final if not _played(performances.get(p.player_id))]
    if not non_players:
        return final, used

    available = sorted(
        (p for p in bench if _played(performances.get(p.player_id))),
        key=lambda p: (p.bench_order, str(p.id)),
    )

    for off in non_players:
        off_position = _position(off)
        for candidate in list(available):
            candidate_position = _position(candidate)

            # The keeper slot is its own thing in both directions.
            if (off_position == "GKP") != (candidate_position == "GKP"):
                continue

            trial = [_position(candidate) if p is off else _position(p) for p in final]
            if not _formation_is_legal(trial):
                continue

            final[final.index(off)] = candidate
            available.remove(candidate)
            used.append(Substitution(off=off, on=candidate))
            break

    return final, used


def _captain_multiplier(selection: TeamSelection) -> int:
    return 3 if selection.active_chip == ChipType.TRIPLE_CAPTAIN else 2


def calculate_selection(
    selection: TeamSelection, *, performances: Optional[Dict] = None
) -> SelectionResult:
    """Work out a gameweek score without writing anything."""
    starters = list(selection.starters.select_related("player").all())
    bench = sorted(
        selection.bench.select_related("player").all(),
        key=lambda p: (p.bench_order, str(p.id)),
    )

    if performances is None:
        player_ids = [p.player_id for p in starters + bench]
        performances = {
            performance.player_id: performance
            for performance in PlayerPerformance.objects.filter(
                player_id__in=player_ids, gameweek=selection.gameweek
            ).select_related("player")
        }

    bench_boost = selection.active_chip == ChipType.BENCH_BOOST

    if bench_boost:
        # Every one of the fifteen scores, so nobody is substituted on.
        counting, substitutions = starters + bench, []
    else:
        counting, substitutions = auto_substitute(starters, bench, performances)

    # The armband moves to the vice-captain only when the captain did not play.
    captain = selection.captain
    if not _played(performances.get(selection.captain.player_id)):
        if _played(performances.get(selection.vice_captain.player_id)):
            captain = selection.vice_captain

    multiplier = _captain_multiplier(selection)

    counted: Dict[object, int] = {}
    gross = 0
    for fantasy_player in counting:
        performance = performances.get(fantasy_player.player_id)
        points = scoring.score_performance(performance) if performance else 0
        if fantasy_player.pkid == captain.pkid and _played(performance):
            points *= multiplier
        counted[fantasy_player.pkid] = points
        gross += points

    transfer_hit = selection.transfer_hit or 0
    return SelectionResult(
        points=gross + transfer_hit,
        gross_points=gross,
        transfer_hit=transfer_hit,
        substitutions=substitutions,
        captain=captain,
        captain_multiplier=multiplier,
        counted=counted,
    )


@transaction.atomic
def recalculate_selection(selection: TeamSelection) -> SelectionResult:
    """Recompute and store one gameweek score."""
    result = calculate_selection(selection)

    selection.points = result.points
    selection.points_calculated_at = timezone.now()
    selection.save(update_fields=["points", "points_calculated_at", "updated_at"])

    if result.substitutions:
        logger.info(
            "GW%s %s: %d automatic substitution(s): %s",
            selection.gameweek.number,
            selection.fantasy_team.name,
            len(result.substitutions),
            ", ".join(
                f"{s.off.player.name} -> {s.on.player.name}"
                for s in result.substitutions
            ),
        )

    recalculate_team_totals(selection.fantasy_team)
    return result


def recalculate_team_totals(team: FantasyTeam) -> int:
    """Set a team's season total to the sum of its gameweek scores.

    Derived rather than accumulated, so it cannot drift from the gameweeks it is
    supposed to be the sum of.
    """
    selections = list(team.selections.all())
    total = sum(selection.points for selection in selections)

    # A player's running total is the sum of what they actually contributed,
    # captain multiplier included, across every gameweek they were counted in.
    per_player: Dict[object, int] = {}
    for selection in selections:
        if selection.points_calculated_at is None:
            continue
        for pkid, points in calculate_selection(selection).counted.items():
            per_player[pkid] = per_player.get(pkid, 0) + points

    for fantasy_player in team.players.all():
        value = per_player.get(fantasy_player.pkid, 0)
        if fantasy_player.total_points != value:
            fantasy_player.total_points = value
            fantasy_player.save(update_fields=["total_points", "updated_at"])

    if team.total_points != total:
        team.total_points = total
        team.save(update_fields=["total_points", "updated_at"])
    return total


def recalculate_gameweek(gameweek) -> int:
    """Recompute every finalised selection in a gameweek. Safe to re-run."""
    selections = TeamSelection.objects.filter(
        gameweek=gameweek, is_finalized=True
    ).select_related("fantasy_team", "captain", "vice_captain", "gameweek")

    count = 0
    for selection in selections:
        try:
            recalculate_selection(selection)
            count += 1
        except Exception:  # noqa: BLE001 - one bad team must not stop the rest
            logger.exception(
                "could not score %s for GW%s",
                selection.fantasy_team.name,
                gameweek.number,
            )
    logger.info("recalculated %d team(s) for GW%s", count, gameweek.number)
    return count
