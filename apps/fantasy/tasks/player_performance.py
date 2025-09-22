import logging
from django.db import transaction

from apps.kpl.models import Player
from apps.fantasy.models import PlayerPerformance
from config.settings import base

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)



def update_player_performance(fixture, home_scorers, away_scorers):
    from apps.kpl.tasks.fixtures import find_player

    PlayerPerformance.objects.filter(fixture=fixture).delete()

    def process_scorers(scorers, scoring_team, opponent_team):
        for player_data in scorers:
            name = player_data["name"].strip()
            if not name:
                continue

            goal_minutes = player_data.get("minutes", [])
            is_own_goal = player_data.get("is_own_goal", False)

            player_obj = find_player(name)

            # If not found, create placeholder player
            if not player_obj:
                team = opponent_team if is_own_goal else scoring_team
                player_obj = Player.objects.create(
                    name=name,
                    team=team,
                    position="FWD",  
                    current_value=6.00 if not is_own_goal else 4.00,
                )
                logger.info(f"Created new player: {name} for team {team.name}")
            else:
                # Ensure player is assigned to the right team
                correct_team = opponent_team if is_own_goal else scoring_team
                if player_obj.team != correct_team:
                    logger.info(f"Reassigning {name}: {player_obj.team.name} → {correct_team.name}")
                    player_obj.team = correct_team
                    player_obj.save(update_fields=["team"])

            performance = PlayerPerformance.objects.create(
                player=player_obj,
                gameweek=fixture.gameweek,
                fixture=fixture,
            )

            if is_own_goal:
                num_own_goals = len(goal_minutes)
                performance.own_goals = num_own_goals
                performance.fantasy_points = -num_own_goals * 2
                logger.info(f"Own goal by {name}: {num_own_goals}")
            else:
                num_goals = len(goal_minutes)
                performance.goals_scored = num_goals
                performance.fantasy_points = num_goals * 4
                performance.minutes_played = 90 if num_goals > 0 else 0
                logger.info(f"Goal by {name}: {num_goals}")

            performance.save()

    with transaction.atomic():
        process_scorers(home_scorers, fixture.home_team, fixture.away_team)
        process_scorers(away_scorers, fixture.away_team, fixture.home_team)

    logger.info(f"Player performances updated for fixture {fixture.id} ({fixture.home_team} vs {fixture.away_team})")

