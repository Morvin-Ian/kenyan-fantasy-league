"""The fantasy scoring rules.

These lock down the bugs found in the three separate copies of the rules that
used to exist, and the rules that were missing entirely.
"""

import pytest

from apps.fantasy import scoring
from apps.fantasy.scoring import Stats


def line(**kwargs) -> Stats:
    return Stats(**kwargs)


# --------------------------------------------------------------------------- #
# Appearance and the 60-minute threshold
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "minutes,expected", [(0, 0), (1, 1), (45, 1), (59, 1), (60, 2), (90, 2)]
)
def test_appearance_points_follow_minutes(minutes, expected):
    assert scoring.score(line(position="MID", minutes_played=minutes)) == expected


# --------------------------------------------------------------------------- #
# Goals, assists, clean sheets
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "position,expected", [("GKP", 6), ("DEF", 6), ("MID", 5), ("FWD", 4)]
)
def test_a_goal_is_worth_more_from_deeper_positions(position, expected):
    scored = line(position=position, minutes_played=90, goals_scored=1)
    blank = line(position=position, minutes_played=90)
    assert scoring.score(scored) - scoring.score(blank) == expected


def test_an_assist_is_three_points_from_anywhere():
    for position in ("GKP", "DEF", "MID", "FWD"):
        with_assist = line(position=position, minutes_played=90, assists=1)
        without = line(position=position, minutes_played=90)
        assert scoring.score(with_assist) - scoring.score(without) == 3


def test_a_midfielder_earns_a_clean_sheet_point():
    """This rule existed in the calculator but was unreachable.

    ``apply_clean_sheets`` only ever set the flag for GKP and DEF, so the
    midfielder branch never ran.
    """
    keeping = line(position="MID", minutes_played=90, clean_sheets=1)
    conceding = line(position="MID", minutes_played=90)
    assert scoring.score(keeping) - scoring.score(conceding) == 1


def test_a_clean_sheet_needs_an_hour_on_the_pitch():
    """A defender on at 85 minutes did not keep the clean sheet."""
    late = line(position="DEF", minutes_played=5, clean_sheets=1)
    full = line(position="DEF", minutes_played=90, clean_sheets=1)
    assert scoring.score(late) == 1  # appearance only
    assert scoring.score(full) == 2 + 4


def test_a_forward_gets_nothing_for_a_clean_sheet():
    assert scoring.score(line(position="FWD", minutes_played=90, clean_sheets=1)) == 2


# --------------------------------------------------------------------------- #
# Goals conceded — a rule that was missing entirely
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "conceded,penalty", [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]
)
def test_keepers_and_defenders_are_docked_per_two_conceded(conceded, penalty):
    for position in ("GKP", "DEF"):
        shipped = line(position=position, minutes_played=90, goals_conceded=conceded)
        assert scoring.score(shipped) == 2 - penalty


def test_midfielders_and_forwards_are_not_docked_for_concessions():
    for position in ("MID", "FWD"):
        shipped = line(position=position, minutes_played=90, goals_conceded=5)
        assert scoring.score(shipped) == 2


# --------------------------------------------------------------------------- #
# Saves — the rounding the incremental path got wrong
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("saves,points", [(0, 0), (2, 0), (3, 1), (5, 1), (6, 2)])
def test_a_keeper_scores_a_point_per_three_saves(saves, points):
    assert (
        scoring.score(line(position="GKP", minutes_played=90, saves=saves))
        == 2 + points
    )


def test_save_points_do_not_depend_on_how_the_stat_arrived():
    """The old incremental path ran ``saves_diff // 3`` on each update.

    Two saves arriving at once scored ``2 // 3 == 0`` and were lost for good.
    Scoring the whole line every time is what makes this correct.
    """
    once = scoring.score(line(position="GKP", minutes_played=90, saves=4))
    in_two_updates = scoring.score(line(position="GKP", minutes_played=90, saves=2))
    in_two_updates = scoring.score(line(position="GKP", minutes_played=90, saves=4))
    assert once == in_two_updates == 2 + 1


# --------------------------------------------------------------------------- #
# Deductions
# --------------------------------------------------------------------------- #


def test_the_deductions():
    base = line(position="MID", minutes_played=90)
    assert (
        scoring.score(line(position="MID", minutes_played=90, yellow_cards=1))
        == scoring.score(base) - 1
    )
    assert (
        scoring.score(line(position="MID", minutes_played=90, red_cards=1))
        == scoring.score(base) - 3
    )
    assert (
        scoring.score(line(position="MID", minutes_played=90, own_goals=1))
        == scoring.score(base) - 2
    )
    assert (
        scoring.score(line(position="MID", minutes_played=90, penalties_missed=1))
        == scoring.score(base) - 2
    )
    assert (
        scoring.score(line(position="GKP", minutes_played=90, penalties_saved=1))
        == scoring.score(line(position="GKP", minutes_played=90)) + 5
    )


def test_a_score_can_be_negative():
    """A red card early in a match outweighs the appearance point.

    ``total_points`` was a PositiveIntegerField, so storing this raised
    IntegrityError and rolled back the whole gameweek update.
    """
    sent_off = line(position="DEF", minutes_played=20, red_cards=1, goals_conceded=4)
    assert scoring.score(sent_off) == 1 - 3 - 2 == -4


# --------------------------------------------------------------------------- #
# A correction has to be able to go down as well as up
# --------------------------------------------------------------------------- #


def test_a_rescinded_card_is_refunded():
    """The old incremental path only ever applied ``if diff > 0``."""
    with_card = line(position="MID", minutes_played=90, red_cards=1)
    rescinded = line(position="MID", minutes_played=90)
    assert scoring.score(with_card) == -1
    assert scoring.score(rescinded) == 2


def test_a_goal_reassigned_to_another_player_is_taken_back():
    credited = line(position="FWD", minutes_played=90, goals_scored=1)
    corrected = line(position="FWD", minutes_played=90, goals_scored=0)
    assert scoring.score(credited) == 6
    assert scoring.score(corrected) == 2


# --------------------------------------------------------------------------- #
# Bonus points
# --------------------------------------------------------------------------- #


def test_bonus_goes_to_the_three_best_in_the_match():
    scores = {"a": 40, "b": 33, "c": 21, "d": 9, "e": 3}
    assert scoring.award_bonus(scores) == {"a": 3, "b": 2, "c": 1}


def test_a_tie_at_the_top_shares_the_higher_award():
    scores = {"a": 40, "b": 40, "c": 21}
    awarded = scoring.award_bonus(scores)
    assert awarded["a"] == awarded["b"] == 3
    assert awarded["c"] == 2


def test_players_who_did_not_feature_get_no_bonus():
    assert scoring.award_bonus({"a": 0, "b": 0}) == {}
    assert "b" not in scoring.award_bonus({"a": 10, "b": 0})


def test_bonus_is_added_to_the_score():
    without = line(position="FWD", minutes_played=90, goals_scored=1)
    with_bonus = line(position="FWD", minutes_played=90, goals_scored=1, bonus=3)
    assert scoring.score(with_bonus) - scoring.score(without) == 3


def test_a_player_who_did_not_play_scores_no_bonus_points():
    assert scoring.bps(line(position="MID", minutes_played=0, goals_scored=1)) == 0


def test_the_bonus_score_rewards_the_actions_that_win_matches():
    striker = line(position="FWD", minutes_played=90, goals_scored=2)
    passenger = line(position="FWD", minutes_played=90)
    assert scoring.bps(striker) > scoring.bps(passenger)

    keeper = line(position="GKP", minutes_played=90, saves=6, clean_sheets=1)
    assert scoring.bps(keeper) > scoring.bps(passenger)


def test_an_unverified_position_is_scored_as_a_midfielder_not_crashed():
    """Half the league carries the unverified MID placeholder."""
    assert scoring.score(line(position=None, minutes_played=90, goals_scored=1)) == 7
    assert scoring.score(line(position="", minutes_played=90, goals_scored=1)) == 7


# --------------------------------------------------------------------------- #
# Explaining a score
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "stats",
    [
        line(position="GKP", minutes_played=90, saves=5, clean_sheets=1, bonus=3),
        line(position="DEF", minutes_played=90, goals_conceded=3, yellow_cards=1),
        line(position="MID", minutes_played=72, goals_scored=1, assists=2),
        line(position="FWD", minutes_played=20, red_cards=1, penalties_missed=1),
        line(position="DEF", minutes_played=10, clean_sheets=1),
        line(position="MID", minutes_played=0),
    ],
)
def test_the_breakdown_always_adds_up_to_the_score(stats):
    """The explanation and the number have to come from the same rules."""
    assert sum(item["points"] for item in scoring.breakdown(stats)) == scoring.score(
        stats
    )


def test_the_breakdown_says_why_a_clean_sheet_did_not_count():
    items = scoring.breakdown(line(position="DEF", minutes_played=10, clean_sheets=1))
    clean_sheet = next(i for i in items if i["label"] == "Clean sheet")
    assert clean_sheet["points"] == 0
    assert "60" in clean_sheet["detail"]


def test_the_breakdown_omits_rules_that_did_not_score():
    items = scoring.breakdown(line(position="MID", minutes_played=90))
    assert [i["label"] for i in items] == ["Played 60+ minutes"]
