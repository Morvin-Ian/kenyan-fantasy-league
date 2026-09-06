"""How the source's free-text roles become POSITION_CHOICES codes.

Every player in the database used to be a midfielder: the squad importer wrote
``position="MID"`` for everyone because the page it read publishes no position.
The club roster pages do publish one, as free text, and these are the strings
they actually use — plus the ones the lineup adapters produce, which go through
the same vocabulary.

The ordering cases are the ones worth guarding. "Defensive Midfielder" contains
both "def" and "mid", and "Wing Back" contains both "wing" and "back"; getting
either the wrong way round silently mis-scores a player every gameweek.
"""

import pytest

from apps.kpl.scraping.normalize import position_code
from apps.kpl.services import map_role_to_position


@pytest.mark.parametrize(
    "label,expected",
    [
        # Exactly the labels the source publishes today.
        ("Goal Keeper", "GKP"),
        ("Defender", "DEF"),
        ("Midfielder", "MID"),
        ("Forward", "FWD"),
        ("Winger", "MID"),
        ("Striker", "FWD"),
        # Spellings other pages and adapters use.
        ("Goalkeeper", "GKP"),
        ("GK", "GKP"),
        ("Keeper", "GKP"),
        ("CB", "DEF"),
        ("Left Back", "DEF"),
        ("Right-Back", "DEF"),
        ("Centre Back", "DEF"),
        ("CDM", "MID"),
        ("Attacking Midfielder", "MID"),
        ("Centre Forward", "FWD"),
        ("Attacker", "FWD"),
        ("CF", "FWD"),
    ],
)
def test_the_labels_the_source_actually_publishes(label, expected):
    assert position_code(label) == expected


@pytest.mark.parametrize(
    "label,expected",
    [
        # "def" and "mid" both appear; the player is a midfielder.
        ("Defensive Midfielder", "MID"),
        ("Defensive midfield", "MID"),
        # "wing" and "back" both appear; the player is a defender.
        ("Wing Back", "DEF"),
        ("Right Wing Back", "DEF"),
        # ... but a winger without "back" is a midfielder, as fantasy scores it.
        ("Right Winger", "MID"),
    ],
)
def test_a_label_naming_two_positions_resolves_to_the_right_one(label, expected):
    assert position_code(label) == expected


@pytest.mark.parametrize("label", ["", "   ", "-", "Coach", "Physio", "Utility", None])
def test_text_that_names_no_position_returns_none_rather_than_a_guess(label):
    """``None`` is what lets the caller record "unverified" instead of "MID"."""
    assert position_code(label) is None


def test_several_weak_hints_are_read_together():
    assert position_code(None, "Goal Keeper") == "GKP"
    assert position_code("11", "Striker") == "FWD"


def test_the_lineup_helper_shares_the_same_vocabulary():
    """Lineups and the squad importer must not disagree about a role."""
    assert map_role_to_position("Goal Keeper") == position_code("Goal Keeper")
    assert map_role_to_position(None, "Defensive Midfielder") == "MID"
    assert map_role_to_position("Coach") is None
