from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from django.utils import timezone

from apps.kpl.models import Fixture, FixtureLineup, Gameweek


class GameweekStatusService:
    """
    Comprehensive service for tracking gameweek status with real-time updates
    """

    def get_comprehensive_gameweek_status(
        self, gameweek_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get complete gameweek status with all interesting metrics
        """
        gameweek = self._get_gameweek(gameweek_id)
        if not gameweek:
            return {"error": "No active gameweek found"}

        fixtures = self._get_gameweek_fixtures(gameweek)

        return {
            "gameweek": {
                "number": gameweek.number,
                "is_active": gameweek.is_active,
                "start_date": gameweek.start_date.isoformat(),
                "end_date": gameweek.end_date.isoformat(),
                "transfer_deadline": gameweek.transfer_deadline.isoformat(),
                "status": self._get_gameweek_status(gameweek, fixtures),
                "progress_percentage": self._calculate_progress_percentage(
                    gameweek, fixtures
                ),
            },
            "match_days": self._get_match_days_status(fixtures),
            "fixtures_summary": self._get_fixtures_summary(fixtures),
            "team_performance": self._get_team_performance_summary(fixtures),
            "interesting_stats": self._get_interesting_stats(gameweek, fixtures),
            "lineups_status": self._get_lineups_status(fixtures),
            "live_updates": self._get_live_updates(fixtures),
        }

    def _get_gameweek(self, gameweek_id: Optional[int] = None) -> Optional[Gameweek]:
        if gameweek_id:
            return Gameweek.objects.filter(id=gameweek_id).first()

        gameweek = Gameweek.objects.filter(is_active=True).first()
        if not gameweek:
            return None

        now = timezone.now().date()
        start_date = gameweek.start_date

        if now < start_date and gameweek.number > 1:
            return Gameweek.objects.filter(number=gameweek.number - 1).first()

        return gameweek

    def _get_gameweek_fixtures(self, gameweek: Gameweek) -> List[Fixture]:
        """Get all fixtures for the gameweek"""
        return list(
            Fixture.objects.filter(gameweek=gameweek)
            .select_related("home_team", "away_team")
            .prefetch_related("lineups")
        )

    def _get_gameweek_status(self, gameweek: Gameweek, fixtures: List[Fixture]) -> str:
        """Determine the overall gameweek status"""
        now = timezone.now()

        # Check if gameweek hasn't started
        if now < timezone.make_aware(
            datetime.combine(gameweek.start_date, datetime.min.time())
        ):
            return "UPCOMING"

        completed_fixtures = [f for f in fixtures if f.status == "completed"]
        postponed_fixtures = [f for f in fixtures if f.status == "postponed"]

        # If all fixtures are either completed or postponed → treat as completed
        if len(completed_fixtures) + len(postponed_fixtures) == len(fixtures):
            return "COMPLETED"

        # Check if any fixture is live
        live_fixtures = [f for f in fixtures if f.status == "live"]
        if live_fixtures:
            return "LIVE"

        # If we're past the end date but some fixtures still pending → delayed
        end_datetime = timezone.make_aware(
            datetime.combine(gameweek.end_date, datetime.max.time())
        )
        if now > end_datetime:
            return "DELAYED"

        return "ACTIVE"

    def _calculate_progress_percentage(
        self, gameweek: Gameweek, fixtures: List[Fixture]
    ) -> int:
        """Calculate gameweek completion percentage (treat postponed as completed)"""
        if not fixtures:
            return 0

        completed = len([f for f in fixtures if f.status == "completed"])
        postponed = len([f for f in fixtures if f.status == "postponed"])

        return int(((completed + postponed) / len(fixtures)) * 100)

    def _get_match_days_status(self, fixtures: List[Fixture]) -> List[Dict[str, Any]]:
        """Group fixtures by match day and get status for each day"""
        match_days = defaultdict(list)

        for fixture in fixtures:
            match_date = fixture.match_date.date()
            match_days[match_date].append(fixture)

        result = []
        for date, day_fixtures in sorted(match_days.items()):
            completed = [f for f in day_fixtures if f.status == "completed"]
            live = [f for f in day_fixtures if f.status == "live"]
            postponed = [f for f in day_fixtures if f.status == "postponed"]

            # Determine match status
            if len(completed) == len(day_fixtures):
                match_status = "COMPLETED"
            elif live:
                match_status = "LIVE"
            elif postponed:
                match_status = "POSTPONED"
            elif any(f.status == "upcoming" for f in day_fixtures):
                match_status = "UPCOMING"
            else:
                match_status = "CONFIRMED"

            # Determine bonus status (you can customize this logic)
            bonus_status = "ADDED" if len(completed) == len(day_fixtures) else "PENDING"

            result.append(
                {
                    "date": date.day,
                    "name": date.strftime("%A"),
                    "month": date.strftime("%b"),
                    "full_date": date.isoformat(),
                    "match_status": match_status,
                    "bonus_status": bonus_status,
                    "fixtures_count": len(day_fixtures),
                    "completed_count": len(completed),
                    "live_count": len(live),
                    "goals_scored": sum(
                        (f.home_team_score or 0) + (f.away_team_score or 0)
                        for f in completed
                    ),
                    "interesting_fact": self._get_day_interesting_fact(day_fixtures),
                }
            )

        return result

    def _get_fixtures_summary(self, fixtures: List[Fixture]) -> Dict[str, Any]:
        """Get summary statistics for all fixtures"""
        completed_fixtures = [f for f in fixtures if f.status == "completed"]

        total_goals = sum(
            (f.home_team_score or 0) + (f.away_team_score or 0)
            for f in completed_fixtures
        )

        home_wins = len(
            [
                f
                for f in completed_fixtures
                if (f.home_team_score or 0) > (f.away_team_score or 0)
            ]
        )
        draws = len(
            [f for f in completed_fixtures if f.home_team_score == f.away_team_score]
        )
        away_wins = len(
            [
                f
                for f in completed_fixtures
                if (f.away_team_score or 0) > (f.home_team_score or 0)
            ]
        )

        return {
            "total_fixtures": len(fixtures),
            "completed": len(completed_fixtures),
            "live": len([f for f in fixtures if f.status == "live"]),
            "upcoming": len([f for f in fixtures if f.status == "upcoming"]),
            "postponed": len([f for f in fixtures if f.status == "postponed"]),
            "total_goals": total_goals,
            "average_goals": (
                round(total_goals / len(completed_fixtures), 2)
                if completed_fixtures
                else 0
            ),
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins,
            "biggest_win": self._get_biggest_win(completed_fixtures),
            "highest_scoring": self._get_highest_scoring_match(completed_fixtures),
        }

    def _get_team_performance_summary(self, fixtures: List[Fixture]) -> Dict[str, Any]:
        """Analyze team performance in this gameweek"""
        completed_fixtures = [f for f in fixtures if f.status == "completed"]
        team_stats = defaultdict(
            lambda: {"played": 0, "goals_for": 0, "goals_against": 0, "points": 0}
        )

        for fixture in completed_fixtures:
            home_goals = fixture.home_team_score or 0
            away_goals = fixture.away_team_score or 0

            # Home team stats
            team_stats[fixture.home_team.name]["played"] += 1
            team_stats[fixture.home_team.name]["goals_for"] += home_goals
            team_stats[fixture.home_team.name]["goals_against"] += away_goals

            # Away team stats
            team_stats[fixture.away_team.name]["played"] += 1
            team_stats[fixture.away_team.name]["goals_for"] += away_goals
            team_stats[fixture.away_team.name]["goals_against"] += home_goals

            # Points calculation
            if home_goals > away_goals:
                team_stats[fixture.home_team.name]["points"] += 3
            elif away_goals > home_goals:
                team_stats[fixture.away_team.name]["points"] += 3
            else:
                team_stats[fixture.home_team.name]["points"] += 1
                team_stats[fixture.away_team.name]["points"] += 1

        # Find interesting teams
        best_attack = (
            max(team_stats.items(), key=lambda x: x[1]["goals_for"])
            if team_stats
            else None
        )
        best_defense = (
            min(team_stats.items(), key=lambda x: x[1]["goals_against"])
            if team_stats
            else None
        )

        return {
            "teams_played": len(
                [team for team, stats in team_stats.items() if stats["played"] > 0]
            ),
            "best_attack": (
                {"team": best_attack[0], "goals": best_attack[1]["goals_for"]}
                if best_attack
                else None
            ),
            "best_defense": (
                {
                    "team": best_defense[0],
                    "goals_conceded": best_defense[1]["goals_against"],
                }
                if best_defense
                else None
            ),
            "team_stats": dict(team_stats),
        }

    def _get_interesting_stats(
        self, gameweek: Gameweek, fixtures: List[Fixture]
    ) -> List[Dict[str, Any]]:
        """Generate interesting statistics and facts"""
        stats = []

        # Goals statistics
        completed_fixtures = [f for f in fixtures if f.status == "completed"]
        total_goals = sum(
            (f.home_team_score or 0) + (f.away_team_score or 0)
            for f in completed_fixtures
        )

        stats.append(
            {
                "label": "Goals Scored",
                "value": str(total_goals),
                "trend": self._compare_to_previous_gameweek(gameweek, "goals"),
            }
        )

        # Clean sheets
        clean_sheets = 0
        for fixture in completed_fixtures:
            if fixture.home_team_score == 0:
                clean_sheets += 1
            if fixture.away_team_score == 0:
                clean_sheets += 1

        stats.append(
            {"label": "Clean Sheets", "value": str(clean_sheets), "trend": "neutral"}
        )

        # Lineup confirmations
        lineups_confirmed = FixtureLineup.objects.filter(
            fixture__in=fixtures, is_confirmed=True
        ).count()

        stats.append(
            {
                "label": "Lineups Confirmed",
                "value": f"{lineups_confirmed}/{len(fixtures) * 2}",
                "trend": "up" if lineups_confirmed > len(fixtures) else "neutral",
            }
        )

        # Add more interesting stats
        stats.extend(self._get_additional_stats(fixtures))

        return stats

    def _get_lineups_status(self, fixtures: List[Fixture]) -> Dict[str, Any]:
        """Get lineup confirmation status"""
        lineup_data = []

        for fixture in fixtures:
            lineups = FixtureLineup.objects.filter(fixture=fixture).select_related(
                "team"
            )
            home_lineup = lineups.filter(side="home").first()
            away_lineup = lineups.filter(side="away").first()

            lineup_data.append(
                {
                    "fixture_id": fixture.id,
                    "home_team": fixture.home_team.name,
                    "away_team": fixture.away_team.name,
                    "match_date": fixture.match_date.isoformat(),
                    "home_lineup_confirmed": (
                        home_lineup.is_confirmed if home_lineup else False
                    ),
                    "away_lineup_confirmed": (
                        away_lineup.is_confirmed if away_lineup else False
                    ),
                    "home_formation": home_lineup.formation if home_lineup else None,
                    "away_formation": away_lineup.formation if away_lineup else None,
                    "status": fixture.status,
                }
            )

        confirmed_lineups = sum(
            1
            for data in lineup_data
            if data["home_lineup_confirmed"] and data["away_lineup_confirmed"]
        )

        return {
            "total_fixtures": len(fixtures),
            "confirmed_lineups": confirmed_lineups,
            "confirmation_percentage": (
                int((confirmed_lineups / len(fixtures)) * 100) if fixtures else 0
            ),
            "lineup_details": lineup_data,
        }

    def _get_live_updates(self, fixtures: List[Fixture]) -> List[Dict[str, Any]]:
        """Get live updates and notifications"""
        updates = []
        now = timezone.now()

        # Live fixtures
        live_fixtures = [f for f in fixtures if f.status == "live"]
        for fixture in live_fixtures:
            updates.append(
                {
                    "type": "live_match",
                    "message": f"{fixture.home_team.name} vs {fixture.away_team.name} is LIVE",
                    "fixture_id": fixture.id,
                    "priority": "high",
                    "timestamp": now.isoformat(),
                }
            )

        upcoming_soon = [
            f
            for f in fixtures
            if f.status == "upcoming" and f.match_date <= now + timedelta(hours=2)
        ]
        for fixture in upcoming_soon:
            minutes_until = int((fixture.match_date - now).total_seconds() / 60)
            updates.append(
                {
                    "type": "upcoming_match",
                    "message": f"{fixture.home_team.name} vs {fixture.away_team.name} starts in {minutes_until} minutes",
                    "fixture_id": fixture.id,
                    "priority": "medium",
                    "timestamp": now.isoformat(),
                }
            )

        # Recently completed
        recently_completed = [
            f
            for f in fixtures
            if f.status == "completed" and f.match_date >= now - timedelta(hours=3)
        ]
        for fixture in recently_completed:
            updates.append(
                {
                    "type": "match_completed",
                    "message": f"{fixture.home_team.name} {fixture.home_team_score}-{fixture.away_team_score} {fixture.away_team.name}",
                    "fixture_id": fixture.id,
                    "priority": "low",
                    "timestamp": now.isoformat(),
                }
            )

        return sorted(updates, key=lambda x: x["priority"], reverse=True)[:10]

    # Helper methods
    def _get_biggest_win(self, fixtures: List[Fixture]) -> Optional[Dict[str, Any]]:
        """Find the biggest win margin"""
        if not fixtures:
            return None

        biggest_margin = 0
        biggest_win = None

        for fixture in fixtures:
            if (
                fixture.home_team_score is not None
                and fixture.away_team_score is not None
            ):
                margin = abs(fixture.home_team_score - fixture.away_team_score)
                if margin > biggest_margin:
                    biggest_margin = margin
                    biggest_win = {
                        "home_team": fixture.home_team.name,
                        "away_team": fixture.away_team.name,
                        "score": f"{fixture.home_team_score}-{fixture.away_team_score}",
                        "margin": margin,
                    }

        return biggest_win

    def _get_highest_scoring_match(
        self, fixtures: List[Fixture]
    ) -> Optional[Dict[str, Any]]:
        """Find the highest scoring match"""
        if not fixtures:
            return None

        highest_goals = 0
        highest_scoring = None

        for fixture in fixtures:
            if (
                fixture.home_team_score is not None
                and fixture.away_team_score is not None
            ):
                total_goals = fixture.home_team_score + fixture.away_team_score
                if total_goals > highest_goals:
                    highest_goals = total_goals
                    highest_scoring = {
                        "home_team": fixture.home_team.name,
                        "away_team": fixture.away_team.name,
                        "score": f"{fixture.home_team_score}-{fixture.away_team_score}",
                        "goals": total_goals,
                    }

        return highest_scoring

    def _get_day_interesting_fact(self, day_fixtures: List[Fixture]) -> str:
        """Generate an interesting fact about the match day"""
        completed = [f for f in day_fixtures if f.status == "completed"]

        if not completed:
            return f"{len(day_fixtures)} fixtures scheduled"

        total_goals = sum(
            (f.home_team_score or 0) + (f.away_team_score or 0) for f in completed
        )

        if total_goals == 0:
            return "Goalless day!"
        elif total_goals >= 15:
            return f"Goal fest! {total_goals} goals"
        else:
            return f"{total_goals} goals scored"

    def _compare_to_previous_gameweek(
        self, current_gameweek: Gameweek, stat_type: str
    ) -> str:
        """Compare statistics to the previous gameweek"""
        return "up"

    def _get_additional_stats(self, fixtures: List[Fixture]) -> List[Dict[str, Any]]:
        """Get additional interesting statistics"""
        stats = []
        return stats
