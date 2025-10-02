import logging

from django.db import transaction

from apps.fantasy.models import PlayerPerformance
from apps.kpl.models import Player
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
                    logger.info(
                        f"Reassigning {name}: {player_obj.team.name} → {correct_team.name}"
                    )
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

    logger.info(
        f"Player performances updated for fixture {fixture.id} ({fixture.home_team} vs {fixture.away_team})"
    )


def update_complete_player_performance(fixture, match_data=None):
    from apps.kpl.tasks.fixtures import find_player
    
    player_stats = {}
    
    def get_or_create_player(name, team, is_own_goal=False):
        name = name.strip()
        if not name:
            return None
            
        player_obj = find_player(name)
        
        if not player_obj:
            player_obj = Player.objects.create(
                name=name,
                team=team,
                position="FWD",  # Default, should be updated manually
                current_value=6.00 if not is_own_goal else 4.00,
            )
            logger.info(f"Created new player: {name} for team {team.name}")
        else:
            # Ensure correct team assignment
            if player_obj.team != team:
                logger.info(f"Reassigning {name}: {player_obj.team.name} → {team.name}")
                player_obj.team = team
                player_obj.save(update_fields=["team"])
        
        return player_obj
    
    def init_player_stats(player_obj):
        """Initialize stats dictionary for a player"""
        if player_obj.id not in player_stats:
            player_stats[player_obj.id] = {
                'player': player_obj,
                'goals_scored': 0,
                'assists': 0,
                'own_goals': 0,
                'yellow_cards': 0,
                'red_cards': 0,
                'minutes_played': 0,
                'clean_sheets': 0,
                'saves': 0,
                'penalties_saved': 0,
                'penalties_missed': 0,
            }
        return player_stats[player_obj.id]
    
    def process_scorers(scorers, scoring_team, opponent_team):
        if not scorers:
            return
            
        for player_data in scorers:
            if isinstance(player_data, str):
                name = player_data
                is_own_goal = False
                goal_count = 1
            else:
                name = player_data.get("name", "").strip()
                is_own_goal = player_data.get("is_own_goal", False)
                goal_minutes = player_data.get("minutes", [])
                goal_count = len(goal_minutes) if goal_minutes else 1
            
            if not name:
                continue
            
            correct_team = opponent_team if is_own_goal else scoring_team
            player_obj = get_or_create_player(name, correct_team, is_own_goal)
            
            if player_obj:
                stats = init_player_stats(player_obj)
                if is_own_goal:
                    stats['own_goals'] += goal_count
                else:
                    stats['goals_scored'] += goal_count
    
    def process_lineup_players(lineup):
        if not lineup:
            return
            
        lineup_players = lineup.players.select_related('player').all()
        for lineup_player in lineup_players:
            player_obj = lineup_player.player
            if player_obj:
                stats = init_player_stats(player_obj)
                stats['minutes_played'] = 90 if not lineup_player.is_bench else 0
    
    def apply_clean_sheets(fixture):
        home_goals = fixture.home_score or 0
        away_goals = fixture.away_score or 0
        
        if away_goals == 0:
            for player_id, stats in player_stats.items():
                player = stats['player']
                if (player.team == fixture.home_team and 
                    stats['minutes_played'] >= 60 and
                    player.position in ['DEF', 'GKP']):
                    stats['clean_sheets'] = 1
        
        if home_goals == 0:
            for player_id, stats in player_stats.items():
                player = stats['player']
                if (player.team == fixture.away_team and 
                    stats['minutes_played'] >= 60 and
                    player.position in ['DEF', 'GKP']):
                    stats['clean_sheets'] = 1
    
    def calculate_fantasy_points(stats, position):
        points = 0
        
        if stats['minutes_played'] > 0:
            points += 1
        if stats['minutes_played'] >= 60:
            points += 1
        
        if position == 'GKP':
            points += stats['goals_scored'] * 6
        elif position == 'DEF':
            points += stats['goals_scored'] * 6
        elif position == 'MID':
            points += stats['goals_scored'] * 5
        else:  
            points += stats['goals_scored'] * 4
        
        points += stats['assists'] * 3
        
        if position in ['GKP', 'DEF']:
            points += stats['clean_sheets'] * 4
        elif position == 'MID':
            points += stats['clean_sheets'] * 1
        
        # Saves (GKP only, every 3 saves = 1 point)
        if position == 'GKP':
            points += (stats['saves'] // 3)
        
        points += stats['penalties_saved'] * 5
        
        points -= stats['penalties_missed'] * 2
        
        points -= stats['own_goals'] * 2
        
        points -= stats['yellow_cards'] * 1
        
        points -= stats['red_cards'] * 3
        
        return points
    
    with transaction.atomic():
        PlayerPerformance.objects.filter(fixture=fixture).delete()
        
        if hasattr(fixture, 'home_scorers') and fixture.home_scorers:
            process_scorers(fixture.home_scorers, fixture.home_team, fixture.away_team)
        if hasattr(fixture, 'away_scorers') and fixture.away_scorers:
            process_scorers(fixture.away_scorers, fixture.away_team, fixture.home_team)
        
        # Process lineups
        try:
            home_lineup = fixture.lineups.filter(team=fixture.home_team).first()
            away_lineup = fixture.lineups.filter(team=fixture.away_team).first()
            
            if home_lineup:
                process_lineup_players(home_lineup)
            if away_lineup:
                process_lineup_players(away_lineup)
        except Exception as e:
            logger.warning(f"Could not process lineups: {str(e)}")
        
        if match_data:
            if 'home_assists' in match_data:
                for player_name in match_data['home_assists']:
                    player_obj = get_or_create_player(player_name, fixture.home_team)
                    if player_obj:
                        stats = init_player_stats(player_obj)
                        stats['assists'] += 1
            
            if 'away_assists' in match_data:
                for player_name in match_data['away_assists']:
                    player_obj = get_or_create_player(player_name, fixture.away_team)
                    if player_obj:
                        stats = init_player_stats(player_obj)
                        stats['assists'] += 1
            
            for card_type in ['yellow_cards', 'red_cards']:
                if card_type in match_data:
                    for player_name in match_data[card_type].get('home', []):
                        player_obj = get_or_create_player(player_name, fixture.home_team)
                        if player_obj:
                            stats = init_player_stats(player_obj)
                            stats[card_type] += 1
                    
                    for player_name in match_data[card_type].get('away', []):
                        player_obj = get_or_create_player(player_name, fixture.away_team)
                        if player_obj:
                            stats = init_player_stats(player_obj)
                            stats[card_type] += 1
            
            for stat_type in ['saves', 'penalties_saved', 'penalties_missed']:
                if stat_type in match_data:
                    home_data = match_data[stat_type].get('home', {})
                    away_data = match_data[stat_type].get('away', {})
                    
                    if isinstance(home_data, dict):
                        for player_name, count in home_data.items():
                            player_obj = get_or_create_player(player_name, fixture.home_team)
                            if player_obj:
                                stats = init_player_stats(player_obj)
                                stats[stat_type] += count
                    
                    if isinstance(away_data, dict):
                        for player_name, count in away_data.items():
                            player_obj = get_or_create_player(player_name, fixture.away_team)
                            if player_obj:
                                stats = init_player_stats(player_obj)
                                stats[stat_type] += count
        
        apply_clean_sheets(fixture)
        
        performance_count = 0
        for player_id, stats in player_stats.items():
            player_obj = stats['player']
            fantasy_points = calculate_fantasy_points(stats, player_obj.position)
            
            PlayerPerformance.objects.create(
                player=player_obj,
                gameweek=fixture.gameweek,
                fixture=fixture,
                goals_scored=stats['goals_scored'],
                assists=stats['assists'],
                own_goals=stats['own_goals'],
                yellow_cards=stats['yellow_cards'],
                red_cards=stats['red_cards'],
                minutes_played=stats['minutes_played'],
                clean_sheets=stats['clean_sheets'],
                saves=stats['saves'],
                penalties_saved=stats['penalties_saved'],
                penalties_missed=stats['penalties_missed'],
                fantasy_points=fantasy_points,
            )
            
            performance_count += 1
            logger.info(
                f"Updated performance for {player_obj.name}: "
                f"{stats['goals_scored']}G, {stats['assists']}A, "
                f"{stats['minutes_played']}min, {fantasy_points} pts"
            )
        
        logger.info(
            f"Created {performance_count} player performances for fixture {fixture.id} "
            f"({fixture.home_team} vs {fixture.away_team})"
        )
        
        return performance_count