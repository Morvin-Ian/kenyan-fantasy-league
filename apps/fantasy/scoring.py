"""The single source of truth for fantasy points.

Before this module the rules lived in three places — ``calculate_fantasy_points``
in ``tasks/player_performance.py``, and ``FantasyPointsCalculator.calculate_full``
and ``.calculate_incremental`` in ``kpl/services/match_events.py``. They had
already drifted apart:

* the incremental path only applied a rule when a stat went **up**
  (``if diff > 0``), so a rescinded card or a goal reassigned to another player
  was never refunded;
* it also ran integer division per delta, so saves going 2 -> 4 scored
  ``2 // 3 == 0`` where a full recalculation scores ``4 // 3 == 1``;
* ``apply_clean_sheets`` only ever set ``clean_sheets`` for GKP and DEF, so the
  midfielder clean-sheet point in the calculators was unreachable.

There is now one rule table and one function. Points are always recomputed from
the whole performance rather than accumulated from deltas, which is what makes a
correction — upward or downward — land correctly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

# --------------------------------------------------------------------------- #
# The rule table
# --------------------------------------------------------------------------- #

MINUTES_FOR_APPEARANCE = 1
MINUTES_FOR_FULL_APPEARANCE = 60

APPEARANCE_POINTS = 1
FULL_APPEARANCE_POINTS = 1

GOAL_POINTS = {"GKP": 6, "DEF": 6, "MID": 5, "FWD": 4}
ASSIST_POINTS = 3
CLEAN_SHEET_POINTS = {"GKP": 4, "DEF": 4, "MID": 1, "FWD": 0}

# A clean sheet is only earned by someone who was on the pitch long enough to
# have helped keep it.
CLEAN_SHEET_MIN_MINUTES = 60

# Goalkeepers and defenders lose a point for every second goal conceded.
GOALS_CONCEDED_POSITIONS = {"GKP", "DEF"}
GOALS_CONCEDED_PER_POINT = 2

SAVES_PER_POINT = 3
PENALTY_SAVE_POINTS = 5
PENALTY_MISS_POINTS = -2
OWN_GOAL_POINTS = -2
YELLOW_CARD_POINTS = -1
RED_CARD_POINTS = -3

TRANSFER_HIT_POINTS = -4

DEFAULT_POSITION = "MID"


def _position(value: Optional[str]) -> str:
    """Normalise a position, falling back to MID for an unverified player."""
    return value if value in GOAL_POINTS else DEFAULT_POSITION


@dataclass(frozen=True)
class Stats:
    """The inputs to a score, independent of how they were stored.

    ``PlayerPerformance`` rows and the plain dictionaries the match importers
    build both convert into this, so the rules only ever see one shape.
    """

    position: str = DEFAULT_POSITION
    minutes_played: int = 0
    goals_scored: int = 0
    assists: int = 0
    clean_sheets: int = 0
    goals_conceded: int = 0
    saves: int = 0
    penalties_saved: int = 0
    penalties_missed: int = 0
    own_goals: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    # Combined clearances, blocks, interceptions and tackles. Only used by the
    # bonus-point score; zero when the source does not publish them.
    defensive_actions: int = 0
    key_passes: int = 0
    # Awarded after every player in the match has been scored, so it is an input
    # here rather than something :func:`score` can work out on its own.
    bonus: int = 0

    @classmethod
    def from_performance(cls, performance) -> "Stats":
        player = getattr(performance, "player", None)
        return cls(
            position=_position(getattr(player, "position", None)),
            minutes_played=performance.minutes_played or 0,
            goals_scored=performance.goals_scored or 0,
            assists=performance.assists or 0,
            clean_sheets=performance.clean_sheets or 0,
            goals_conceded=getattr(performance, "goals_conceded", 0) or 0,
            saves=performance.saves or 0,
            penalties_saved=performance.penalties_saved or 0,
            penalties_missed=performance.penalties_missed or 0,
            own_goals=performance.own_goals or 0,
            yellow_cards=performance.yellow_cards or 0,
            red_cards=performance.red_cards or 0,
            defensive_actions=getattr(performance, "defensive_actions", 0) or 0,
            key_passes=getattr(performance, "key_passes", 0) or 0,
            bonus=getattr(performance, "bonus", 0) or 0,
        )

    @classmethod
    def from_dict(cls, data: Dict, position: Optional[str] = None) -> "Stats":
        known = {f for f in cls.__dataclass_fields__ if f != "position"}
        return cls(
            position=_position(position or data.get("position")),
            **{key: data.get(key, 0) or 0 for key in known},
        )


# --------------------------------------------------------------------------- #
# Points
# --------------------------------------------------------------------------- #


def score(stats: Stats) -> int:
    """Points for one player in one match, before any captain multiplier.

    Always computed from the complete stat line. Never accumulate this from
    deltas — that is what made corrections unreliable.
    """
    position = _position(stats.position)
    points = 0

    if stats.minutes_played >= MINUTES_FOR_APPEARANCE:
        points += APPEARANCE_POINTS
    if stats.minutes_played >= MINUTES_FOR_FULL_APPEARANCE:
        points += FULL_APPEARANCE_POINTS

    points += stats.goals_scored * GOAL_POINTS[position]
    points += stats.assists * ASSIST_POINTS

    # The 60-minute requirement is enforced here as well as at the point the
    # clean sheet is recorded, so a stat line edited by hand in the admin cannot
    # award a clean sheet to a player who came on in stoppage time.
    if stats.clean_sheets and stats.minutes_played >= CLEAN_SHEET_MIN_MINUTES:
        points += stats.clean_sheets * CLEAN_SHEET_POINTS[position]

    if position in GOALS_CONCEDED_POSITIONS:
        points -= stats.goals_conceded // GOALS_CONCEDED_PER_POINT

    if position == "GKP":
        points += stats.saves // SAVES_PER_POINT

    points += stats.penalties_saved * PENALTY_SAVE_POINTS
    points += stats.penalties_missed * PENALTY_MISS_POINTS
    points += stats.own_goals * OWN_GOAL_POINTS
    points += stats.yellow_cards * YELLOW_CARD_POINTS
    points += stats.red_cards * RED_CARD_POINTS

    points += stats.bonus

    return points


def score_performance(performance) -> int:
    """Points for a stored ``PlayerPerformance`` row."""
    return score(Stats.from_performance(performance))


# --------------------------------------------------------------------------- #
# Bonus points
# --------------------------------------------------------------------------- #

# The bonus-point score. Every player in a match is scored on the actions below,
# then the three highest in that match take 3, 2 and 1 bonus points.
BPS_APPEARANCE = 3
BPS_FULL_APPEARANCE = 6
BPS_GOAL = {"GKP": 12, "DEF": 12, "MID": 18, "FWD": 24}
BPS_ASSIST = 9
BPS_CLEAN_SHEET = {"GKP": 12, "DEF": 12, "MID": 0, "FWD": 0}
BPS_SAVE = 2
BPS_PENALTY_SAVE = 15
BPS_PENALTY_MISS = -6
BPS_OWN_GOAL = -6
BPS_YELLOW = -3
BPS_RED = -9
BPS_GOALS_CONCEDED_PER_POINT = 2
BPS_GOALS_CONCEDED = -4
BPS_DEFENSIVE_ACTION = 1
BPS_KEY_PASS = 1

BONUS_AWARDS = [3, 2, 1]


def bps(stats: Stats) -> int:
    """The bonus-point score for one player in one match.

    Deliberately a different scale to :func:`score`: it exists only to rank
    players within a single match, so the absolute number is never shown.
    """
    position = _position(stats.position)
    if stats.minutes_played < MINUTES_FOR_APPEARANCE:
        return 0

    total = BPS_APPEARANCE
    if stats.minutes_played >= MINUTES_FOR_FULL_APPEARANCE:
        total += BPS_FULL_APPEARANCE - BPS_APPEARANCE

    total += stats.goals_scored * BPS_GOAL[position]
    total += stats.assists * BPS_ASSIST
    if stats.clean_sheets and stats.minutes_played >= CLEAN_SHEET_MIN_MINUTES:
        total += BPS_CLEAN_SHEET[position]
    total += stats.saves * BPS_SAVE
    total += stats.penalties_saved * BPS_PENALTY_SAVE
    total += stats.penalties_missed * BPS_PENALTY_MISS
    total += stats.own_goals * BPS_OWN_GOAL
    total += stats.yellow_cards * BPS_YELLOW
    total += stats.red_cards * BPS_RED

    if position in GOALS_CONCEDED_POSITIONS:
        total += (
            stats.goals_conceded // BPS_GOALS_CONCEDED_PER_POINT
        ) * BPS_GOALS_CONCEDED

    total += stats.defensive_actions * BPS_DEFENSIVE_ACTION
    total += stats.key_passes * BPS_KEY_PASS
    return total


def award_bonus(scores: Dict[object, int]) -> Dict[object, int]:
    """Turn ``{key: bps}`` for one match into ``{key: bonus points}``.

    Ties share the higher award and do not consume the place below, which is how
    a shared top score gives two players 3 points and the next player 1.
    Everyone who scored nothing is left out rather than recorded as a zero.
    """
    ranked = sorted({value for value in scores.values() if value > 0}, reverse=True)
    if not ranked:
        return {}

    tier_for_value = {}
    for index, value in enumerate(ranked[: len(BONUS_AWARDS)]):
        tier_for_value[value] = BONUS_AWARDS[index]

    return {
        key: tier_for_value[value]
        for key, value in scores.items()
        if value in tier_for_value
    }


# --------------------------------------------------------------------------- #
# Explaining a score
# --------------------------------------------------------------------------- #


def breakdown(stats: Stats) -> List[Dict]:
    """Itemise a score into the lines that produced it.

    Built from the same rule table as :func:`score`, so the two cannot disagree,
    and it is asserted against it in the tests. Only rules that actually scored
    are listed — a player with no card does not need a line saying so.
    """
    position = _position(stats.position)
    lines: List[Dict] = []

    def add(label: str, points: int, detail: str = "", force: bool = False) -> None:
        # Zero-point rules are left out — a player with no card needs no line
        # saying so — except where the zero is the thing worth explaining.
        if points or force:
            lines.append({"label": label, "points": points, "detail": detail})

    if stats.minutes_played >= MINUTES_FOR_FULL_APPEARANCE:
        add(
            "Played 60+ minutes",
            APPEARANCE_POINTS + FULL_APPEARANCE_POINTS,
            f"{stats.minutes_played} min",
        )
    elif stats.minutes_played >= MINUTES_FOR_APPEARANCE:
        add("Appearance", APPEARANCE_POINTS, f"{stats.minutes_played} min")

    add(
        "Goals",
        stats.goals_scored * GOAL_POINTS[position],
        f"{stats.goals_scored} x {GOAL_POINTS[position]}" if stats.goals_scored else "",
    )
    add(
        "Assists",
        stats.assists * ASSIST_POINTS,
        f"{stats.assists} x {ASSIST_POINTS}" if stats.assists else "",
    )

    if stats.clean_sheets and stats.minutes_played >= CLEAN_SHEET_MIN_MINUTES:
        add("Clean sheet", stats.clean_sheets * CLEAN_SHEET_POINTS[position])
    elif stats.clean_sheets:
        add("Clean sheet", 0, f"needs {CLEAN_SHEET_MIN_MINUTES} min", force=True)

    if position in GOALS_CONCEDED_POSITIONS and stats.goals_conceded:
        add(
            "Goals conceded",
            -(stats.goals_conceded // GOALS_CONCEDED_PER_POINT),
            f"{stats.goals_conceded} conceded",
        )

    if position == "GKP" and stats.saves:
        add("Saves", stats.saves // SAVES_PER_POINT, f"{stats.saves} saves")

    add("Penalties saved", stats.penalties_saved * PENALTY_SAVE_POINTS)
    add("Penalties missed", stats.penalties_missed * PENALTY_MISS_POINTS)
    add("Own goals", stats.own_goals * OWN_GOAL_POINTS)
    add("Yellow cards", stats.yellow_cards * YELLOW_CARD_POINTS)
    add("Red card", stats.red_cards * RED_CARD_POINTS)
    add("Bonus", stats.bonus)

    return lines


def breakdown_for(performance) -> List[Dict]:
    return breakdown(Stats.from_performance(performance))
