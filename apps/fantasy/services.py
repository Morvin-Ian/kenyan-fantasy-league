from apps.accounts.models import User
from .models import FantasyPlayer

from .models import FantasyTeam


class FantasyService:
    @staticmethod
    def create_fantasy_team(user: User, data: dict) -> FantasyTeam:
        return FantasyTeam.objects.create(user=user, **data)

    @staticmethod
    def update_fantasy_team(team: FantasyTeam, data: dict) -> FantasyTeam:
        for key, value in data.items():
            setattr(team, key, value)

        team.save()
        return team

    @staticmethod
    def delete_fantasy_team(team: FantasyTeam) -> None:
        team.delete()
        
    @staticmethod
    def bulk_create_players(players_data: list, fantasy_team: FantasyTeam) -> list:
        players = [FantasyPlayer(**data, fantasy_team=fantasy_team) for data in players_data]
        return FantasyPlayer.objects.bulk_create(players)
