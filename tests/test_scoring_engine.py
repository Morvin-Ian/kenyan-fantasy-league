"""Gameweek scoring: auto-substitutions, the armband, and chips.

Each of these covers something that was either wrong or entirely absent:

* the captain's points were never doubled in the stored total — the code
  worked out a ``role`` label and then added the undoubled score;
* Triple Captain and Bench Boost were applied in the serializer only, so a
  chip changed what the user saw and never what they banked;
* there were no automatic substitutions at all, so a starter who did not play
  simply cost you the points.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.fantasy.models import (
    ChipType,
    FantasyPlayer,
    FantasyTeam,
    PlayerPerformance,
    TeamSelection,
)
from apps.fantasy.services import scoring_engine
from apps.kpl.models import Fixture, Gameweek, Player, Team

SQUAD = (
    [("GKP", "Keeper One")]
    + [("DEF", f"Defender {i}") for i in range(1, 6)]
    + [("MID", f"Midfielder {i}") for i in range(1, 6)]
    + [("FWD", f"Forward {i}") for i in range(1, 4)]
)
# 1 GKP, 5 DEF, 5 MID, 3 FWD = 14; plus a reserve keeper = 15.


@pytest.fixture
def squad(db):
    # Spread across clubs: a squad may hold at most three players from any one
    # real team, which FantasyPlayer.clean() enforces on every save.
    clubs = [
        Team.objects.create(
            name=f"Test Club {i}", logo_url="https://example.test/l.png"
        )
        for i in range(6)
    ]
    club = clubs[0]
    user = User.objects.create_user(
        username="manager",
        email="m@example.test",
        password="pw",
        first_name="A",
        last_name="Manager",
    )
    team = FantasyTeam.objects.create(user=user, name="Test XI", formation="3-4-3")
    gameweek = Gameweek.objects.create(
        number=1,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=7),
        transfer_deadline=timezone.now() + timedelta(days=1),
        is_active=True,
    )
    fixture = Fixture.objects.create(
        home_team=club,
        away_team=club,
        match_date=timezone.now(),
        venue="Test Ground",
        status="completed",
        gameweek=gameweek,
    )

    players = {}
    for index, (position, name) in enumerate(SQUAD + [("GKP", "Keeper Two")]):
        player = Player.objects.create(
            name=name,
            team=clubs[index % len(clubs)],
            position=position,
            position_source="manual",
        )
        players[name] = FantasyPlayer.objects.create(
            fantasy_team=team, player=player, purchase_price=5, current_value=5
        )
    return {
        "team": team,
        "gameweek": gameweek,
        "fixture": fixture,
        "players": players,
    }


def perform(squad, name, **stats):
    return PlayerPerformance.objects.create(
        player=squad["players"][name].player,
        gameweek=squad["gameweek"],
        fixture=squad["fixture"],
        **stats,
    )


def select(squad, starters, bench, captain, vice, chip=None, transfer_hit=0):
    players = squad["players"]
    selection = TeamSelection.objects.create(
        fantasy_team=squad["team"],
        gameweek=squad["gameweek"],
        formation="3-4-3",
        captain=players[captain],
        vice_captain=players[vice],
        is_finalized=True,
        active_chip=chip,
        transfer_hit=transfer_hit,
    )
    selection.starters.set([players[n] for n in starters])
    for order, name in enumerate(bench, start=1):
        fantasy_player = players[name]
        fantasy_player.bench_order = order
        fantasy_player.save(update_fields=["bench_order"])
    selection.bench.set([players[n] for n in bench])
    return selection


ELEVEN = [
    "Keeper One",
    "Defender 1",
    "Defender 2",
    "Defender 3",
    "Midfielder 1",
    "Midfielder 2",
    "Midfielder 3",
    "Midfielder 4",
    "Forward 1",
    "Forward 2",
    "Forward 3",
]
BENCH = ["Keeper Two", "Defender 4", "Midfielder 5", "Defender 5"]


@pytest.mark.django_db
def test_the_captain_actually_gets_double_points(squad):
    """The stored total used to add the captain's undoubled score."""
    for name in ELEVEN:
        perform(squad, name, minutes_played=90)
    scorer = PlayerPerformance.objects.get(player__name="Forward 1")
    scorer.goals_scored = 1
    scorer.fantasy_points = 0
    scorer.save()

    selection = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Midfielder 1")
    result = scoring_engine.calculate_selection(selection)

    # Forward 1: 2 appearance + 4 goal = 6, doubled = 12.
    assert result.counted[squad["players"]["Forward 1"].pkid] == 12


@pytest.mark.django_db
def test_the_armband_moves_to_the_vice_captain_when_the_captain_is_unused(squad):
    for name in ELEVEN:
        perform(squad, name, minutes_played=0 if name == "Forward 1" else 90)

    selection = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Midfielder 1")
    result = scoring_engine.calculate_selection(selection)

    assert result.captain == squad["players"]["Midfielder 1"]
    assert result.counted[squad["players"]["Midfielder 1"].pkid] == 4  # 2 doubled


@pytest.mark.django_db
def test_triple_captain_is_banked_not_only_displayed(squad):
    for name in ELEVEN:
        perform(squad, name, minutes_played=90)

    plain = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Midfielder 1")
    normal = scoring_engine.calculate_selection(plain).points
    plain.active_chip = ChipType.TRIPLE_CAPTAIN
    plain.save()
    tripled = scoring_engine.calculate_selection(plain).points

    # Forward 1 scores 2, so the extra multiplier is worth exactly 2 more.
    assert tripled - normal == 2


@pytest.mark.django_db
def test_bench_boost_counts_the_bench(squad):
    for name in ELEVEN + BENCH:
        perform(squad, name, minutes_played=90)

    selection = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Midfielder 1")
    without = scoring_engine.calculate_selection(selection).points
    selection.active_chip = ChipType.BENCH_BOOST
    selection.save()
    with_boost = scoring_engine.calculate_selection(selection).points

    assert with_boost - without == 4 * 2  # four bench players, 2 points each


# --------------------------------------------------------------------------- #
# Automatic substitutions
# --------------------------------------------------------------------------- #


@pytest.mark.django_db
def test_a_starter_who_did_not_play_is_replaced_from_the_bench(squad):
    for name in ELEVEN:
        perform(squad, name, minutes_played=0 if name == "Midfielder 1" else 90)
    perform(squad, "Midfielder 5", minutes_played=90, goals_scored=1)

    selection = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Forward 2")
    result = scoring_engine.calculate_selection(selection)

    assert result.auto_subs_made == 1
    assert result.substitutions[0].off.player.name == "Midfielder 1"
    assert result.substitutions[0].on.player.name == "Midfielder 5"
    assert squad["players"]["Midfielder 5"].pkid in result.counted


@pytest.mark.django_db
def test_the_bench_is_used_in_order(squad):
    for name in ELEVEN:
        perform(squad, name, minutes_played=0 if name == "Defender 1" else 90)
    # Both are eligible; bench_order decides.
    perform(squad, "Defender 4", minutes_played=90)
    perform(squad, "Defender 5", minutes_played=90)

    selection = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Forward 2")
    result = scoring_engine.calculate_selection(selection)

    assert result.substitutions[0].on.player.name == "Defender 4"


@pytest.mark.django_db
def test_a_substitution_that_would_break_the_formation_is_not_made(squad):
    """Three at the back is the minimum; a defender cannot be replaced by a
    midfielder if that would leave only two."""
    starters = [
        "Keeper One",
        "Defender 1",
        "Defender 2",
        "Defender 3",
        "Midfielder 1",
        "Midfielder 2",
        "Midfielder 3",
        "Midfielder 4",
        "Forward 1",
        "Forward 2",
        "Forward 3",
    ]
    for name in starters:
        perform(squad, name, minutes_played=0 if name == "Defender 1" else 90)
    # Only a midfielder is available on the bench.
    perform(squad, "Midfielder 5", minutes_played=90)

    selection = select(
        squad,
        starters,
        ["Keeper Two", "Midfielder 5"],
        captain="Forward 1",
        vice="Forward 2",
    )
    result = scoring_engine.calculate_selection(selection)

    assert result.auto_subs_made == 0


@pytest.mark.django_db
def test_only_a_keeper_replaces_the_keeper(squad):
    for name in ELEVEN:
        perform(squad, name, minutes_played=0 if name == "Keeper One" else 90)
    perform(squad, "Keeper Two", minutes_played=90)
    perform(squad, "Defender 4", minutes_played=90)

    selection = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Forward 2")
    result = scoring_engine.calculate_selection(selection)

    assert result.substitutions[0].on.player.name == "Keeper Two"


@pytest.mark.django_db
def test_a_bench_player_who_also_did_not_play_cannot_come_on(squad):
    for name in ELEVEN:
        perform(squad, name, minutes_played=0 if name == "Midfielder 1" else 90)
    perform(squad, "Midfielder 5", minutes_played=0)

    selection = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Forward 2")
    assert scoring_engine.calculate_selection(selection).auto_subs_made == 0


# --------------------------------------------------------------------------- #
# Storage: idempotent, and derived rather than accumulated
# --------------------------------------------------------------------------- #


@pytest.mark.django_db
def test_rescoring_a_gameweek_does_not_double_the_total(squad):
    """Points used to be added onto the running total as events arrived."""
    for name in ELEVEN:
        perform(squad, name, minutes_played=90)
    selection = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Midfielder 1")

    first = scoring_engine.recalculate_selection(selection).points
    second = scoring_engine.recalculate_selection(selection).points

    squad["team"].refresh_from_db()
    assert first == second
    assert squad["team"].total_points == first


@pytest.mark.django_db
def test_a_correction_downward_reduces_the_total(squad):
    for name in ELEVEN:
        perform(squad, name, minutes_played=90)
    scorer = PlayerPerformance.objects.get(player__name="Forward 2")
    scorer.goals_scored = 1
    scorer.save()

    selection = select(squad, ELEVEN, BENCH, captain="Forward 1", vice="Midfielder 1")
    before = scoring_engine.recalculate_selection(selection).points

    # The goal is reassigned to someone in another match.
    scorer.goals_scored = 0
    scorer.save()
    after = scoring_engine.recalculate_selection(selection).points

    squad["team"].refresh_from_db()
    assert before - after == 4
    assert squad["team"].total_points == after


@pytest.mark.django_db
def test_a_transfer_hit_comes_off_the_gameweek_score(squad):
    for name in ELEVEN:
        perform(squad, name, minutes_played=90)
    selection = select(
        squad, ELEVEN, BENCH, captain="Forward 1", vice="Midfielder 1", transfer_hit=-8
    )
    result = scoring_engine.recalculate_selection(selection)

    assert result.transfer_hit == -8
    assert result.points == result.gross_points - 8


@pytest.mark.django_db
def test_a_sent_off_player_does_not_crash_the_update(squad):
    """total_points was a PositiveIntegerField with a CHECK (>= 0)."""
    for name in ELEVEN:
        perform(squad, name, minutes_played=0)
    disgraced = PlayerPerformance.objects.get(player__name="Defender 1")
    disgraced.minutes_played = 10
    disgraced.red_cards = 1
    disgraced.goals_conceded = 6
    disgraced.save()

    selection = select(
        squad, ELEVEN, BENCH, captain="Defender 1", vice="Defender 2", transfer_hit=-12
    )
    result = scoring_engine.recalculate_selection(selection)

    squad["team"].refresh_from_db()
    assert result.points < 0
    assert squad["team"].total_points == result.points
