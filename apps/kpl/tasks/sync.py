"""Celery tasks that pull the Kenyan Premier League into the database.

Source of record is the primary provider (see
``apps.kpl.scraping.providers.primary``). Its host is not named anywhere in the
source tree; it comes from the ``SCRAPER_*`` environment settings.

Every task follows the same three rules:

* **Discover, never hard-code.** The tournament id changes each season, so it is
  looked up from the competition index and cached, not pinned in a constant.
* **Parse everything before writing anything.** The previous standings task
  deleted the table and *then* parsed, so any parse failure left the site with
  no table at all. Here a write only happens once a full, validated snapshot is
  in hand.
* **Key on provider ids.** Clubs, players and matches are matched on the
  source's own stable ids and only fall back to name matching for rows that have
  never been seen before.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from apps.kpl.models import (
    ExternalFixtureMapping,
    ExternalPlayerMapping,
    ExternalTeamMapping,
    Fixture,
    FixtureLineup,
    FixtureLineupPlayer,
    Gameweek,
    Player,
    Standing,
    Team,
    TopcorerData,
)
from apps.kpl.scraping import ScrapeError, StructureChanged
from apps.kpl.scraping.http import fetch_bytes
from apps.kpl.scraping.normalize import player_key, team_key
from apps.kpl.scraping.providers import primary

from .base import scraping_task

logger = logging.getLogger(__name__)

SEASON_CACHE_KEY = "kpl:scrape:current-season"
SEASON_CACHE_TTL = 12 * 60 * 60

# A Kenyan Premier League matchday is one round: every club plays once.
# Used to slice the flat fixture list into gameweeks when the fixtures page
# does not label them (it only labels results).
DEFAULT_CLUB_COUNT = 18

# Transfers close one hour before the first kick-off of the gameweek.
DEADLINE_LEAD = timedelta(hours=1)

# Bench entries share a table with the starting XI under a unique
# (lineup, order_index) constraint, so they are numbered from an offset.
BENCH_ORDER_OFFSET = 100


# --------------------------------------------------------------------------- #
# Season
# --------------------------------------------------------------------------- #


def current_season(*, refresh: bool = False) -> primary.Season:
    """Return the active KPL season, cached so every task does not re-discover."""
    if not refresh:
        cached = cache.get(SEASON_CACHE_KEY)
        if cached:
            return primary.Season(**cached)

    season = primary.discover_current_season()
    cache.set(SEASON_CACHE_KEY, season.__dict__, SEASON_CACHE_TTL)
    return season


def season_period(season: primary.Season) -> str:
    """The ``Standing.period`` label, e.g. ``"2026-2027"``."""
    return f"{season.start_year}-{season.end_year}"


# --------------------------------------------------------------------------- #
# Team resolution
# --------------------------------------------------------------------------- #


def _team_index() -> Tuple[Dict[str, Team], Dict[str, Team]]:
    """Build lookups from provider id and normalised name to Team."""
    by_provider: Dict[str, Team] = {
        mapping.provider_team_id: mapping.team
        for mapping in ExternalTeamMapping.objects.filter(
            provider=primary.PROVIDER
        ).select_related("team")
    }
    by_name: Dict[str, Team] = {
        team_key(team.name): team for team in Team.objects.all()
    }
    return by_provider, by_name


def resolve_team(
    name: str,
    provider_id: Optional[str],
    *,
    by_provider: Dict[str, Team],
    by_name: Dict[str, Team],
) -> Optional[Team]:
    """Find the Team for a scraped club, preferring the provider's own id."""
    if provider_id and provider_id in by_provider:
        return by_provider[provider_id]
    return by_name.get(team_key(name))


# --------------------------------------------------------------------------- #
# Teams and logos
# --------------------------------------------------------------------------- #


@scraping_task(name="apps.kpl.tasks.sync.sync_teams")
def sync_teams():
    """Create/refresh the 18 competing clubs and flag everyone else relegated."""
    season = current_season()
    scraped = primary.fetch_teams(season.tournament_id)

    if len(scraped) < 10:
        raise StructureChanged(
            f"only {len(scraped)} clubs found for {season.label}; refusing to "
            "rewrite the club list from an obviously partial page"
        )

    by_provider, by_name = _team_index()
    created = updated = 0
    active_ids: List[int] = []

    with transaction.atomic():
        for row in scraped:
            team = resolve_team(
                row.name, row.provider_id, by_provider=by_provider, by_name=by_name
            )
            if team is None:
                team = Team.objects.create(
                    name=row.name, logo_url=row.logo_url or "", is_relegated=False
                )
                created += 1
                logger.info("created club %s (%s)", row.name, row.provider_id)
            else:
                changed = False
                if row.logo_url and team.logo_url != row.logo_url:
                    team.logo_url = row.logo_url
                    changed = True
                if team.is_relegated:
                    team.is_relegated = False
                    changed = True
                    logger.info("club %s is back in the top flight", team.name)
                if changed:
                    team.save(update_fields=["logo_url", "is_relegated", "updated_at"])
                    updated += 1

            ExternalTeamMapping.objects.update_or_create(
                provider=primary.PROVIDER,
                provider_team_id=row.provider_id,
                defaults={"team": team},
            )
            active_ids.append(team.pkid)

        relegated = Team.objects.exclude(pkid__in=active_ids).filter(is_relegated=False)
        relegated_names = list(relegated.values_list("name", flat=True))
        relegated.update(is_relegated=True)

    logger.info(
        "teams synced for %s: %d created, %d updated, %d marked relegated",
        season.label,
        created,
        updated,
        len(relegated_names),
    )
    return {
        "season": season.label,
        "active": len(active_ids),
        "created": created,
        "updated": updated,
        "relegated": relegated_names,
    }


@scraping_task(name="apps.kpl.tasks.sync.sync_team_logos")
def sync_team_logos(force: bool = False):
    """Mirror each club badge into local media.

    The upstream host serves the badges directly, but it is a single small box.
    Caching the file locally means the UI keeps its badges when that host is
    unreachable or moves its media paths.
    """
    downloaded = skipped = failed = 0

    for team in Team.objects.filter(is_relegated=False).exclude(logo_url=""):
        if team.logo_image and not force:
            skipped += 1
            continue
        try:
            content, content_type = fetch_bytes(team.logo_url)
        except ScrapeError as exc:
            logger.warning("could not download badge for %s: %s", team.name, exc)
            failed += 1
            continue

        # The source stores some badges with a truncated ".peg" extension.
        extension = "png" if "png" in content_type else "jpg"
        filename = f"{team_key(team.name) or team.pkid}.{extension}"
        team.logo_image.save(filename, ContentFile(content), save=True)
        downloaded += 1
        logger.info("cached badge for %s (%d bytes)", team.name, len(content))

    return {"downloaded": downloaded, "skipped": skipped, "failed": failed}


# --------------------------------------------------------------------------- #
# Standings
# --------------------------------------------------------------------------- #


@scraping_task(name="apps.kpl.tasks.sync.sync_standings")
def sync_standings():
    """Replace the league table with a freshly scraped, validated snapshot.

    The table is only swapped once every row has been parsed *and* matched to a
    club, so a parse failure or a source redesign leaves the existing table
    intact instead of blanking it.
    """
    season = current_season()
    rows = primary.fetch_standings(season.tournament_id)

    if not rows:
        logger.info("no league table published yet for %s", season.label)
        return {"season": season.label, "rows": 0, "reason": "table not published yet"}

    by_provider, by_name = _team_index()
    snapshot: List[Standing] = []
    unmatched: List[str] = []
    period = season_period(season)

    for row in rows:
        team = resolve_team(
            row.team_name,
            row.provider_team_id,
            by_provider=by_provider,
            by_name=by_name,
        )
        if team is None:
            unmatched.append(row.team_name)
            continue
        snapshot.append(
            Standing(
                team=team,
                position=row.position,
                played=row.played,
                wins=row.wins,
                draws=row.draws,
                losses=row.losses,
                goals_for=row.goals_for,
                goals_against=row.goals_against,
                goal_differential=row.goal_differential,
                points=row.points,
                period=period,
            )
        )

    if unmatched:
        # Every club in the table should already exist; if not, sync_teams has
        # not run yet and swapping now would drop rows from the table.
        raise StructureChanged(
            f"{len(unmatched)} clubs in the league table have no Team row "
            f"({', '.join(unmatched[:5])}); run sync_teams first"
        )

    with transaction.atomic():
        Standing.objects.all().delete()
        Standing.objects.bulk_create(snapshot)

    logger.info(
        "league table for %s replaced with %d rows", season.label, len(snapshot)
    )
    return {"season": season.label, "rows": len(snapshot), "period": period}


# --------------------------------------------------------------------------- #
# Gameweeks and fixtures
# --------------------------------------------------------------------------- #


def _assign_matchdays(
    fixtures: List[primary.FixtureRow], *, club_count: int
) -> List[Tuple[int, primary.FixtureRow]]:
    """Pair each fixture with a matchday number.

    The fixtures page groups matches by date only, so matchdays are rebuilt by
    walking the season in kick-off order and closing a round once every club has
    played once. Rows that already carry an explicit matchday (the results page
    labels them) keep it.
    """
    per_round = max(1, club_count // 2)
    ordered = sorted(fixtures, key=lambda f: (f.kickoff, f.home_team))

    assigned: List[Tuple[int, primary.FixtureRow]] = []
    matchday = 1
    in_round = 0

    for fixture in ordered:
        if fixture.matchday:
            assigned.append((fixture.matchday, fixture))
            continue
        if in_round >= per_round:
            matchday += 1
            in_round = 0
        assigned.append((matchday, fixture))
        in_round += 1

    return assigned


def _upsert_gameweeks(
    assigned: List[Tuple[int, primary.FixtureRow]]
) -> Dict[int, Gameweek]:
    """Create or move the Gameweek rows implied by the fixture calendar."""
    windows: Dict[int, List[datetime]] = {}
    for matchday, fixture in assigned:
        windows.setdefault(matchday, []).append(fixture.kickoff)

    gameweeks: Dict[int, Gameweek] = {}
    for matchday, kickoffs in sorted(windows.items()):
        first, last = min(kickoffs), max(kickoffs)
        deadline = first - DEADLINE_LEAD
        if timezone.is_naive(deadline):
            deadline = timezone.make_aware(deadline)

        gameweek = Gameweek.objects.filter(number=matchday).first()
        if gameweek is None:
            gameweek = Gameweek.objects.create(
                number=matchday,
                start_date=first.date(),
                end_date=last.date(),
                transfer_deadline=deadline,
            )
            logger.info(
                "created gameweek %d (%s to %s)", matchday, first.date(), last.date()
            )
        else:
            changed = False
            for field, value in (
                ("start_date", first.date()),
                ("end_date", last.date()),
            ):
                if getattr(gameweek, field) != value:
                    setattr(gameweek, field, value)
                    changed = True
            # Never move a deadline that has already passed — managers have
            # already made decisions against it.
            if (
                not gameweek.is_deadline_passed
                and gameweek.transfer_deadline != deadline
            ):
                gameweek.transfer_deadline = deadline
                changed = True
            if changed:
                gameweek.save()
        gameweeks[matchday] = gameweek

    return gameweeks


@scraping_task(name="apps.kpl.tasks.sync.sync_fixtures")
def sync_fixtures():
    """Import the season calendar: gameweeks, fixtures and their provider ids."""
    season = current_season()
    scraped = primary.fetch_fixtures(season.tournament_id)
    if not scraped:
        raise StructureChanged(f"no fixtures parsed for {season.label}")

    by_provider, by_name = _team_index()
    club_count = max(
        DEFAULT_CLUB_COUNT, Team.objects.filter(is_relegated=False).count()
    )
    assigned = _assign_matchdays(scraped, club_count=club_count)
    gameweeks = _upsert_gameweeks(assigned)

    existing = {
        mapping.provider_fixture_id: mapping.fixture
        for mapping in ExternalFixtureMapping.objects.filter(
            provider=primary.PROVIDER
        ).select_related("fixture")
    }

    created = updated = skipped = 0
    now = timezone.now()

    for matchday, row in assigned:
        home = resolve_team(
            row.home_team,
            row.home_provider_id,
            by_provider=by_provider,
            by_name=by_name,
        )
        away = resolve_team(
            row.away_team,
            row.away_provider_id,
            by_provider=by_provider,
            by_name=by_name,
        )
        if home is None or away is None:
            logger.warning(
                "skipping fixture %s vs %s: club not in database",
                row.home_team,
                row.away_team,
            )
            skipped += 1
            continue

        kickoff = row.kickoff
        if timezone.is_naive(kickoff):
            kickoff = timezone.make_aware(kickoff)

        fixture = (
            existing.get(row.provider_fixture_id) if row.provider_fixture_id else None
        )
        if fixture is None:
            # Fall back to the natural key so a fixture added before mappings
            # existed is adopted rather than duplicated.
            fixture = Fixture.objects.filter(
                home_team=home, away_team=away, match_date=kickoff
            ).first()

        gameweek = gameweeks.get(matchday)

        if fixture is None:
            fixture = Fixture.objects.create(
                home_team=home,
                away_team=away,
                match_date=kickoff,
                venue=row.venue or "Unknown",
                gameweek=gameweek,
                status="upcoming" if kickoff >= now else "completed",
            )
            created += 1
        else:
            changed_fields = []
            # A finished match keeps its recorded kick-off; only the schedule
            # ahead of us is allowed to move.
            if (
                fixture.status in {"upcoming", "postponed"}
                and fixture.match_date != kickoff
            ):
                fixture.match_date = kickoff
                changed_fields.append("match_date")
            if row.venue and fixture.venue != row.venue:
                fixture.venue = row.venue
                changed_fields.append("venue")
            if gameweek and fixture.gameweek_id != gameweek.pkid:
                fixture.gameweek = gameweek
                changed_fields.append("gameweek")
            if changed_fields:
                fixture.save(update_fields=[*changed_fields, "updated_at"])
                updated += 1

        if row.provider_fixture_id:
            ExternalFixtureMapping.objects.update_or_create(
                provider=primary.PROVIDER,
                provider_fixture_id=row.provider_fixture_id,
                defaults={"fixture": fixture},
            )

    logger.info(
        "fixtures synced for %s: %d created, %d updated, %d skipped, %d gameweeks",
        season.label,
        created,
        updated,
        skipped,
        len(gameweeks),
    )
    return {
        "season": season.label,
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "gameweeks": len(gameweeks),
    }


@scraping_task(name="apps.kpl.tasks.sync.sync_results")
def sync_results():
    """Write final scores onto played fixtures and mark them completed."""
    season = current_season()
    results = primary.fetch_results(season.tournament_id)
    if not results:
        logger.info("no results published yet for %s", season.label)
        return {"season": season.label, "updated": 0}

    by_provider, by_name = _team_index()
    updated = created = unmatched = 0

    for row in results:
        home = resolve_team(
            row.home_team,
            row.home_provider_id,
            by_provider=by_provider,
            by_name=by_name,
        )
        away = resolve_team(
            row.away_team,
            row.away_provider_id,
            by_provider=by_provider,
            by_name=by_name,
        )
        if home is None or away is None:
            unmatched += 1
            continue

        fixture = _find_fixture_for_result(row, home, away)
        if fixture is None:
            # The source removes a match from the fixtures page once it has been
            # played, so anything finished before our first calendar sync has no
            # scheduled row to attach to. Create it, otherwise a mid-season
            # deployment silently loses every result played to date.
            fixture = _create_fixture_from_result(row, home, away)
            created += 1

        changed = []
        if fixture.home_team_score != row.home_score:
            fixture.home_team_score = row.home_score
            changed.append("home_team_score")
        if fixture.away_team_score != row.away_score:
            fixture.away_team_score = row.away_score
            changed.append("away_team_score")
        if fixture.status != "completed":
            fixture.status = "completed"
            changed.append("status")
        if changed:
            fixture.save(update_fields=[*changed, "updated_at"])
            updated += 1

        if row.provider_score_id:
            ExternalFixtureMapping.objects.update_or_create(
                provider=primary.MATCH_PROVIDER,
                provider_fixture_id=row.provider_score_id,
                defaults={"fixture": fixture},
            )

    logger.info(
        "results synced for %s: %d fixtures updated, %d back-filled, %d unmatched",
        season.label,
        updated,
        created,
        unmatched,
    )
    return {
        "season": season.label,
        "updated": updated,
        "created": created,
        "unmatched": unmatched,
    }


def _create_fixture_from_result(
    row: primary.FixtureRow, home: Team, away: Team
) -> Fixture:
    """Back-fill a fixture for a result that has no scheduled row.

    Used when a match was played before this installation first scraped the
    calendar. The matchday label on the results page gives the gameweek; without
    one the fixture is left unassigned for the next calendar sync to place.
    """
    kickoff = row.kickoff
    if timezone.is_naive(kickoff):
        kickoff = timezone.make_aware(kickoff)

    gameweek = (
        Gameweek.objects.filter(number=row.matchday).first() if row.matchday else None
    )
    if gameweek is None and row.matchday:
        gameweek = Gameweek.objects.create(
            number=row.matchday,
            start_date=kickoff.date(),
            end_date=kickoff.date(),
            transfer_deadline=kickoff - DEADLINE_LEAD,
        )

    fixture, _ = Fixture.objects.get_or_create(
        home_team=home,
        away_team=away,
        match_date=kickoff,
        defaults={
            "venue": row.venue or "Unknown",
            "gameweek": gameweek,
            "status": "completed",
        },
    )
    logger.info(
        "back-filled fixture %s vs %s on %s from a published result",
        home.name,
        away.name,
        kickoff.date(),
    )
    return fixture


def _find_fixture_for_result(
    row: primary.FixtureRow, home: Team, away: Team
) -> Optional[Fixture]:
    """Locate the scheduled fixture a result belongs to.

    The results page carries a match-report id rather than the scheduled-fixture
    id used by the calendar, and the date can differ from the original schedule
    when a match is moved, so this matches on the clubs and then takes the
    nearest date within a fortnight.
    """
    if row.provider_score_id:
        mapping = (
            ExternalFixtureMapping.objects.filter(
                provider=primary.MATCH_PROVIDER,
                provider_fixture_id=row.provider_score_id,
            )
            .select_related("fixture")
            .first()
        )
        if mapping:
            return mapping.fixture

    kickoff = row.kickoff
    if timezone.is_naive(kickoff):
        kickoff = timezone.make_aware(kickoff)

    candidates = list(
        Fixture.objects.filter(
            home_team=home,
            away_team=away,
            match_date__range=(
                kickoff - timedelta(days=14),
                kickoff + timedelta(days=14),
            ),
        )
    )
    if not candidates:
        return None
    return min(candidates, key=lambda f: abs(f.match_date - kickoff))


# --------------------------------------------------------------------------- #
# Players
# --------------------------------------------------------------------------- #


@scraping_task(name="apps.kpl.tasks.sync.sync_players", lock_ttl=45 * 60)
def sync_players():
    """Import every registered squad for the current season.

    The source publishes names and its own player ids but no positions or ages,
    so an existing player's position is never overwritten here; newly discovered
    players are created as midfielders for a human to correct.
    """
    season = current_season()
    squads = primary.fetch_squads(season.tournament_id)

    by_provider, by_name = _team_index()
    mapped = {
        mapping.provider_player_id: mapping.player
        for mapping in ExternalPlayerMapping.objects.filter(
            provider=primary.PROVIDER
        ).select_related("player")
    }

    created = moved = linked = 0
    unmatched_clubs: List[str] = []

    for squad in squads:
        team = resolve_team(
            squad.team_name,
            squad.provider_team_id,
            by_provider=by_provider,
            by_name=by_name,
        )
        if team is None:
            unmatched_clubs.append(squad.team_name)
            continue

        squad_names = {player_key(p.name): p for p in squad.players}
        existing_by_key = {
            player_key(p.name): p for p in Player.objects.filter(team=team)
        }

        with transaction.atomic():
            for entry in squad.players:
                player = mapped.get(entry.provider_player_id)
                if player is None:
                    player = existing_by_key.get(player_key(entry.name))

                if player is None:
                    player = Player.objects.create(
                        name=entry.name, team=team, position="MID"
                    )
                    created += 1
                elif player.team_id != team.pkid:
                    # A transfer: the squad page is authoritative on who plays
                    # where, so follow it rather than duplicating the player.
                    logger.info(
                        "moving %s from %s to %s",
                        player.name,
                        player.team.name,
                        team.name,
                    )
                    player.team = team
                    player.save(update_fields=["team", "updated_at"])
                    moved += 1

                if entry.provider_player_id:
                    _, was_created = ExternalPlayerMapping.objects.update_or_create(
                        provider=primary.PROVIDER,
                        provider_player_id=entry.provider_player_id,
                        defaults={"player": player},
                    )
                    linked += int(was_created)

        logger.info("%s: %d players in squad", team.name, len(squad_names))

    if unmatched_clubs:
        logger.warning("squads with no matching club: %s", unmatched_clubs)

    return {
        "season": season.label,
        "squads": len(squads),
        "players_created": created,
        "players_moved": moved,
        "ids_linked": linked,
        "unmatched_clubs": unmatched_clubs,
    }


# --------------------------------------------------------------------------- #
# Top scorers
# --------------------------------------------------------------------------- #


@scraping_task(name="apps.kpl.tasks.sync.sync_top_scorers")
def sync_top_scorers(gameweek_id: Optional[str] = None, limit: int = 20):
    """Snapshot the scoring charts against a gameweek."""
    season = current_season()

    gameweek = (
        Gameweek.objects.filter(pkid=gameweek_id).first()
        if gameweek_id
        else Gameweek.objects.filter(is_active=True).first()
    )
    if gameweek is None:
        gameweek = Gameweek.objects.order_by("-number").first()
    if gameweek is None:
        logger.warning("no gameweek exists yet; run sync_fixtures first")
        return {"success": False, "error": "no gameweek available"}

    scorers = primary.fetch_scorers(season.tournament_id, limit=limit)
    if not scorers:
        logger.info("no goals recorded yet for %s", season.label)
        return {"success": True, "gameweek": gameweek.number, "count": 0}

    mapped = {
        mapping.provider_player_id: mapping.player
        for mapping in ExternalPlayerMapping.objects.filter(
            provider=primary.PROVIDER,
            provider_player_id__in=[
                s.provider_player_id for s in scorers if s.provider_player_id
            ],
        ).select_related("player")
    }

    saved = 0
    with transaction.atomic():
        for row in scorers:
            TopcorerData.objects.update_or_create(
                gameweek=gameweek,
                player_name=row.player_name,
                defaults={
                    "team_name": row.team_name,
                    "goals": row.goals,
                    "rank": row.rank,
                    "player": mapped.get(row.provider_player_id),
                },
            )
            saved += 1

    logger.info(
        "saved %d scorers for gameweek %d (%s)", saved, gameweek.number, season.label
    )
    return {"success": True, "gameweek": gameweek.number, "count": saved}


# --------------------------------------------------------------------------- #
# Match detail
# --------------------------------------------------------------------------- #


@scraping_task(name="apps.kpl.tasks.sync.sync_match_details", lock_ttl=45 * 60)
def sync_match_details(limit: int = 20):
    """Settle finished matches from their published match report.

    Reads goals, cards and both lineups from the match report and hands the events
    to :class:`~apps.kpl.services.match_events.MatchEventService`, which owns
    deduplication and fantasy points. This is a post-match settlement path — the
    report appears after the final whistle, not during play.
    """
    from apps.kpl.services.match_events import MatchEventService

    season = current_season()
    results = [
        row for row in primary.fetch_results(season.tournament_id) if row.is_played
    ]
    if not results:
        return {"season": season.label, "processed": 0}

    by_provider, by_name = _team_index()
    processed = failed = 0

    for row in results[:limit]:
        if not row.provider_score_id:
            continue

        home = resolve_team(
            row.home_team,
            row.home_provider_id,
            by_provider=by_provider,
            by_name=by_name,
        )
        away = resolve_team(
            row.away_team,
            row.away_provider_id,
            by_provider=by_provider,
            by_name=by_name,
        )
        if home is None or away is None:
            continue

        fixture = _find_fixture_for_result(row, home, away)
        if fixture is None:
            continue

        try:
            detail = primary.fetch_match_detail(row.provider_score_id)
        except ScrapeError as exc:
            logger.warning(
                "could not read match report %s: %s", row.provider_score_id, exc
            )
            failed += 1
            continue

        goals = [
            {
                "player_name": goal.player_name,
                "team_id": (home if goal.team_side == "home" else away).id,
                "count": 1,
                "minute": goal.minute or 0,
            }
            for goal in detail.goals
        ]
        yellows, reds = [], []
        for card in detail.cards:
            target = resolve_team(
                card.team_name, None, by_provider=by_provider, by_name=by_name
            )
            payload = {
                "player_name": card.player_name,
                "team_id": (target or home).id,
                "count": 1,
                "minute": card.minute or 0,
            }
            (yellows if card.card == "yellow" else reds).append(payload)

        if goals:
            MatchEventService.update_goals(fixture, goals)
        if yellows or reds:
            MatchEventService.update_cards(fixture, yellows, reds)

        _store_lineups(fixture, home, away, detail)
        processed += 1

    logger.info("settled %d match reports (%d failed)", processed, failed)
    return {"season": season.label, "processed": processed, "failed": failed}


def _store_lineups(
    fixture: Fixture, home: Team, away: Team, detail: primary.MatchDetail
) -> None:
    """Persist both published lineups against the fixture."""
    sides = (
        ("home", home, detail.home_starters, detail.home_bench),
        ("away", away, detail.away_starters, detail.away_bench),
    )

    for side, team, starters, bench in sides:
        if not starters:
            continue

        with transaction.atomic():
            lineup, _ = FixtureLineup.objects.update_or_create(
                fixture=fixture,
                team=team,
                side=side,
                defaults={
                    "is_confirmed": True,
                    "source": primary.PROVIDER,
                    "published_at": timezone.now(),
                },
            )
            lineup.players.all().delete()

            entries = [
                *((index, name, False) for index, name in enumerate(starters, start=1)),
                *(
                    (BENCH_ORDER_OFFSET + index, name, True)
                    for index, name in enumerate(bench, start=1)
                ),
            ]
            FixtureLineupPlayer.objects.bulk_create(
                [
                    FixtureLineupPlayer(
                        lineup=lineup,
                        player=_match_squad_player(name, team),
                        order_index=order,
                        is_bench=is_bench,
                    )
                    for order, name, is_bench in entries
                ]
            )


def _match_squad_player(name: str, team: Team) -> Optional[Player]:
    """Resolve a lineup name to a Player already registered with that club."""
    key = player_key(name)
    for player in Player.objects.filter(team=team):
        if player_key(player.name) == key:
            return player
    return None


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


@scraping_task(name="apps.kpl.tasks.sync.sync_all", lock_ttl=60 * 60)
def sync_all():
    """Run the full pipeline in dependency order, in one worker slot.

    Clubs first (everything else resolves against them), then the calendar, then
    the data that hangs off it. Each step is reported independently so one
    failure does not hide the steps that succeeded.
    """
    steps = (
        ("teams", sync_teams),
        ("logos", sync_team_logos),
        ("fixtures", sync_fixtures),
        ("players", sync_players),
        ("results", sync_results),
        ("standings", sync_standings),
        ("scorers", sync_top_scorers),
    )

    report: Dict[str, object] = {}
    for label, task in steps:
        try:
            # Call the underlying function directly: this is already inside a
            # worker, and each step takes its own lock.
            report[label] = task.run()
        except Exception as exc:  # noqa: BLE001 - one bad step must not stop the rest
            logger.exception("sync_all step '%s' failed", label)
            report[label] = {"error": f"{type(exc).__name__}: {exc}"}

    return report
