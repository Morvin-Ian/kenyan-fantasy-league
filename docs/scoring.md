# How fantasy points work

Every rule lives in `apps/fantasy/scoring.py`. Nothing else is allowed a copy:
the rules previously existed in three places (`calculate_fantasy_points` in the
performance importer, and `calculate_full`/`calculate_incremental` in the match
event service) and had drifted apart, which is how a midfielder's clean-sheet
point became unreachable and a goalkeeper's save points went missing.

Points are always recomputed from the whole stat line, never accumulated from
deltas. That is what makes a correction work in both directions.

## The rules

| Rule | GKP | DEF | MID | FWD |
| --- | --- | --- | --- | --- |
| Playing 1–59 minutes | 1 | 1 | 1 | 1 |
| Playing 60+ minutes | 2 | 2 | 2 | 2 |
| Goal | 6 | 6 | 5 | 4 |
| Assist | 3 | 3 | 3 | 3 |
| Clean sheet (60+ min only) | 4 | 4 | 1 | – |
| Every 2 goals conceded | −1 | −1 | – | – |
| Every 3 saves | 1 | – | – | – |
| Penalty saved | 5 | 5 | 5 | 5 |
| Penalty missed | −2 | −2 | −2 | −2 |
| Own goal | −2 | −2 | −2 | −2 |
| Yellow card | −1 | −1 | −1 | −1 |
| Red card | −3 | −3 | −3 | −3 |
| Transfer beyond the free allowance | −4 each |

A player whose position has never been verified is scored as a midfielder; see
the `position_source` section of `docs/scraping.md` for how to find them.

## Bonus points

Every player in a match is given a bonus score — a different scale, used only to
rank within that match — and the three highest take 3, 2 and 1 points. A tie
shares the higher award. Players who did not appear score nothing and are left
out rather than recorded as a zero.

The score rewards the actions that decide matches: goals (weighted by position),
assists, clean sheets, saves, penalties saved, and defensive actions and key
passes where the source publishes them. Cards, own goals and goals conceded
count against it.

`defensive_actions` (clearances, blocks, interceptions and tackles combined) and
`key_passes` are on `PlayerPerformance` and read as zero until a source
publishes them, which simply makes bonus turn on goals, assists and saves.

## A gameweek score

`apps/fantasy/services/scoring_engine.py` turns a finalised `TeamSelection` into
a score, in this order:

1. **Automatic substitutions.** A starter who played no minutes is replaced by
   the first bench player, in `bench_order`, who did play — but only where the
   resulting eleven is still a legal shape (3–5 defenders, 2–5 midfielders, 1–3
   forwards), and only a keeper ever replaces the keeper.
2. **The armband.** The captain's points are doubled, or tripled under a Triple
   Captain chip. If the captain played no minutes the armband moves to the
   vice-captain.
3. **Chips.** Bench Boost counts all fifteen and makes no substitutions.
4. **Transfer hits.** Deducted from the gameweek, not from the manager's money.

The result is stored on `TeamSelection.points`, and a team's season total is the
sum of its gameweek scores. It is derived rather than accumulated, so it cannot
drift from the gameweeks it is supposed to be the sum of, and rescoring a
gameweek is safe to repeat.

Because the total is derived, a deploy that introduces this needs one rescore:
existing selections carry the column default of 0, so until they are scored a
team's derived total is lower than the total it accumulated under the old
scheme, and the first match event to touch that team writes the lower number.

    python manage.py rescore --dry-run   # report what would change
    python manage.py rescore             # every gameweek with a selection

It is safe to re-run at any time — nothing is accumulated, and it never writes
to `PlayerPerformance`, which is what it reads.

`scoring.breakdown()` itemises a score into the lines that produced it. It is
built from the same rule table and asserted against `score()` in the tests, so
the explanation shown in the player modal cannot disagree with the number.

## Where the stats come from

| Stat | Source |
| --- | --- |
| Goals, own goals, cards | primary source match report |
| Clean sheets, goals conceded | derived from the final score |
| Minutes played | see the caveat below |
| Assists, saves, penalties | entered by hand, or a richer source |
| Defensive actions, key passes | not currently published |

**Minutes are the weak link.** The primary source does not publish them, so a
starter is recorded as having played 90 and a substitute 0, adjusted only where
a substitution event was captured. That makes the 60-minute threshold and the
clean-sheet rule approximate for anyone substituted. A source that publishes
real minutes would fix the appearance points, the clean-sheet rule and the
automatic substitutions in one go, and is the single most valuable thing to add.
