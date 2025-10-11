from datetime import datetime
from collections import defaultdict
from django.utils import timezone
from ..models import Gameweek, PlayerPerformance


class TeamOfTheWeekService:
    @staticmethod
    def get_gameweek(gameweek_number=None):
        if gameweek_number:
            return Gameweek.objects.filter(number=gameweek_number).first()

        gameweek = Gameweek.objects.filter(is_active=True).first()
        if gameweek:
            now = timezone.now().datet()
            start_date = gameweek.start_date
            if now < start_date and gameweek.number > 1:
                gameweek = Gameweek.objects.filter(number=gameweek.number - 1).first()
        return gameweek

    @staticmethod
    def get_team_of_the_week(gameweek):
        performances = (
            PlayerPerformance.objects.filter(gameweek=gameweek)
            .select_related("player", "player__team")
        )

        if not performances.exists():
            return None

        def get_top_players(position):
            return list(
                performances.filter(player__position=position)
                .order_by("-fantasy_points")
            )

        def select_with_team_limit(players, required, team_counts):
            selected = []
            for p in players:
                if len(selected) >= required:
                    break
                team = p.player.team.name if p.player.team else "Unknown"
                if team_counts.get(team, 0) < 3:
                    selected.append(p)
                    team_counts[team] = team_counts.get(team, 0) + 1
            return selected, team_counts

        team_counts = {}
        gkps, team_counts = select_with_team_limit(get_top_players("GKP"), 1, team_counts)
        defs, team_counts = select_with_team_limit(get_top_players("DEF"), 4, team_counts)
        mids, team_counts = select_with_team_limit(get_top_players("MID"), 4, team_counts)
        fwds, team_counts = select_with_team_limit(get_top_players("FWD"), 2, team_counts)

        total_selected = gkps + defs + mids + fwds

        # Fill remaining if less than 11
        if len(total_selected) < 11:
            selected_ids = {p.player.id for p in total_selected}
            remaining = performances.exclude(player_id__in=selected_ids).order_by("-fantasy_points")

            for p in remaining:
                if len(total_selected) >= 11:
                    break
                team = p.player.team.name if p.player.team else "Unknown"
                if team_counts.get(team, 0) < 3:
                    total_selected.append(p)
                    team_counts[team] = team_counts.get(team, 0) + 1

        # Final hard enforcement
        final_team_counts = defaultdict(int)
        final_selected = []

        for p in total_selected:
            team = p.player.team.name if p.player.team else "Unknown"
            if final_team_counts[team] < 3:
                final_selected.append(p)
                final_team_counts[team] += 1
            if len(final_selected) >= 11:
                break

        # Split by position
        def filter_pos(pos, limit):
            return [p for p in final_selected if p.player.position == pos][:limit]

        result = {
            "goalkeeper": filter_pos("GKP", 1),
            "defenders": filter_pos("DEF", 5),
            "midfielders": filter_pos("MID", 5),
            "forwards": filter_pos("FWD", 3),
            "team_counts": dict(final_team_counts),
            "complete": len(final_selected) == 11,
        }
        return result

    @staticmethod
    def serialize_player(perf):
        return {
            "player_id": perf.player.id,
            "name": perf.player.name,
            "team": perf.player.team.name if perf.player.team else None,
            "position": perf.player.position,
            "fantasy_points": perf.fantasy_points,
            "goals_scored": perf.goals_scored,
            "assists": perf.assists,
            "clean_sheets": perf.clean_sheets,
            "saves": perf.saves,
            "minutes_played": perf.minutes_played,
        }

    @classmethod
    def serialize_team(cls, team_data, gameweek_number):
        return {
            "gameweek": gameweek_number,
            "complete": team_data["complete"],
            "team_distribution": team_data["team_counts"],
            "goalkeeper": [cls.serialize_player(p) for p in team_data["goalkeeper"]],
            "defenders": [cls.serialize_player(p) for p in team_data["defenders"]],
            "midfielders": [cls.serialize_player(p) for p in team_data["midfielders"]],
            "forwards": [cls.serialize_player(p) for p in team_data["forwards"]],
        }
