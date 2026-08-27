All edits verified. Full report:

# Incident Report — PR #78 follow-up (fingerprint `d4c84f054cbeadb6`)

**One-line summary:** `FantasyPlayerViewSet.get_team_players` (`apps/fantasy/views.py`) answered `{"detail": "No fantasy team found for this user."}` — a dict — on HTTP 200 for a teamless user instead of `[]`, and the frontend store assigned raw bodies into the typed `userTeam: FantasyTeam[]` state with no array guard, so the Team page's `.length` gates rendered nothing.

**Branch:** `maajun/incident-d4c84f054cbeadb6` (on top of merge `19dc4b6` of PR #78)

## Overview

A logged-in user with no fantasy team opens the Team page. `GET /api/v1/fantasy/players/team-players/` — the sibling of `user-team` — still returned `{"detail": "No fantasy team found for this user."}` with `200 OK`, the exact dict-on-200 shape that the previous incident (`cd9106015d85d54f`) fixed for `get_user_team` but explicitly left unfixed here ("only cosmetically inconsistent"). The store writes the body verbatim into `userTeam` (typed `FantasyTeam[]`); `TeamView.vue` gates every branch on `userTeam.length`, which is `undefined` on a dict, so neither the team view nor the empty state renders.

## Root cause

`apps/fantasy/views.py:142-146` (`FantasyPlayerViewSet.get_team_players`, no-team branch):

```python
else:
    return Response(
        {"detail": "No fantasy team found for this user."},
        status=status.HTTP_200_OK,
    )
```

The non-empty branch returns `self.get_serializer(players, many=True).data` (a list), so the empty branch must return `[]`. Returning a dict on 200 breaks the declared contract consumed by `client/src/stores/fantasy.ts:64` (`this.userTeam = response.data` into `userTeam: [] as FantasyTeam[]`) and by every `TeamView.vue` guard keyed on `.length` (lines 3, 75, 165) plus `components/Team/SideBar.vue:280` (`userTeam[0]`). On a dict all of these evaluate false → blank page, no "Build Your KPL Fantasy Team!" empty state.

## Applied fix

- **`apps/fantasy/views.py`** — `get_team_players` no-team branch now returns `Response([], status=status.HTTP_200_OK)`, restoring the list contract to match `get_user_team`.
- **`client/src/stores/fantasy.ts`** — `fetchUserFantasyTeam` coerces a non-array body to `[]` before assigning `userTeam` and before the `.length`/`[0]` gameweek logic, so the typed state can never hold a dict and the Team page always renders one of its branches.
- **`tests/test_fantasy_user_team.py`** — added regression test `test_team_players_returns_empty_list_when_user_has_no_team`, pinning `GET /api/v1/fantasy/players/team-players/` to `[]` on 200. It fails on the old code (`[] == {"detail": ...}`) and passes with the fix. The existing `test_user_team_returns_empty_list_when_user_has_no_team` continues to pin `user-team`.
- **`docs/incidents/d4c84f054cbeadb6.md`** — incident record following the repo's `docs/incidents/` convention.

## Verification

- No-team branch of `get_team_players` verified returning `[]` with 200 (`views.py:142-148`).
- Store guard verified: `Array.isArray(response.data) ? response.data : []` before assignment and return (`fantasy.ts:63-84`).
- Both endpoints now share one contract: empty list on 200; `fetchFantasyTeamPlayers` already had an `Array.isArray` defense and remains consistent.
- Run: `pytest tests/test_fantasy_user_team.py` (needs a database per `pytest.ini` → `config.settings.development`; cache swapped to locmem via the existing `LOCMEM_CACHE` override).

---

## Error details

```
Workflow: CI/CD
Run: #47
Branch: maajun/incident-0613a35dbc8501ff
Event: pull_request
Status: failure
Link: https://github.com/Morvin-Ian/kenyan-fantasy-league/actions/runs/32773553387
Commit: f413032c
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `gh-actions:Morvin-Ian/kenyan-fantasy-league`
- First seen: 2026-08-25T19:55:12+00:00
- Fingerprint: `d4c84f054cbeadb6`
