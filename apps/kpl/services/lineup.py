import logging
from typing import Dict, List, Optional
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.kpl.models import Fixture, Team, Player, FixtureLineup, FixtureLineupPlayer
from apps.fantasy.models import PlayerPerformance

logger = logging.getLogger(__name__)


class LineupService:
    """Service for handling lineup operations"""

    @staticmethod
    @transaction.atomic
    def submit_manual_lineup(lineup_data: Dict, auto_update_performance: bool = True) -> Dict:
        """
        Submit a manual lineup for a fixture
        """
        try:
            fixture = get_object_or_404(Fixture, id=lineup_data['fixture_id'])
            team = get_object_or_404(Team, id=lineup_data['team_id'])
            
            starting_xi = lineup_data.get('starting_xi', [])
            if len(starting_xi) != 11:
                raise ValueError("Starting XI must have exactly 11 players")
            
            formation = lineup_data.get('formation', '4-4-2')
            if not LineupService._validate_formation(formation, starting_xi):
                raise ValueError("Formation does not match player positions")
            
            side = lineup_data.get('side')
            if not side:
                side = 'home' if fixture.home_team == team else 'away'
            
            existing_lineup = FixtureLineup.objects.filter(
                fixture=fixture, 
                team=team
            ).first()
            
            if existing_lineup:
                lineup = existing_lineup
                lineup.formation = formation
                lineup.is_confirmed = True
                lineup.source = 'manual'
                lineup.side = side
                lineup.save()
                
                lineup.players.all().delete()
            else:
                lineup = FixtureLineup.objects.create(
                    fixture=fixture,
                    team=team,
                    side=side,
                    formation=formation,
                    is_confirmed=True,
                    source='manual'
                )
            
            order_index = 0
            starters_to_create_performance = []
            lineup_players_to_create = []
            
            # Create starting XI players
            for i, player_id in enumerate(starting_xi):
                player = get_object_or_404(Player, id=player_id)
                lineup_players_to_create.append(
                    FixtureLineupPlayer(
                        lineup=lineup,
                        player=player,
                        position=player.position,
                        order_index=order_index,
                        is_bench=False
                    )
                )
                starters_to_create_performance.append(player)
                order_index += 1
            
            bench_players = lineup_data.get('bench_players', [])
            for i, player_id in enumerate(bench_players):
                player = get_object_or_404(Player, id=player_id)
                lineup_players_to_create.append(
                    FixtureLineupPlayer(
                        lineup=lineup,
                        player=player,
                        position=player.position,
                        order_index=order_index,
                        is_bench=True
                    )
                )
                order_index += 1
            
            FixtureLineupPlayer.objects.bulk_create(lineup_players_to_create)
            
            starters_performance_created = 0
            if fixture.gameweek and starters_to_create_performance:
                starters_performance_created = LineupService._create_starter_performances(
                    starters_to_create_performance, fixture
                )
            
            performance_count = 0
            if auto_update_performance:
                try:
                    from apps.fantasy.tasks.player_performance import (
                        update_complete_player_performance,
                    )

                    home_lineup_exists = fixture.lineups.filter(
                        team=fixture.home_team
                    ).exists()
                    away_lineup_exists = fixture.lineups.filter(
                        team=fixture.away_team
                    ).exists()

                    if home_lineup_exists and away_lineup_exists:
                        performance_count = update_complete_player_performance(fixture)

                except Exception as e:
                    logger.error(f"Error updating player performances: {str(e)}")
            
            return {
                "status": "success",
                "message": "Lineup submitted successfully",
                "lineup_id": lineup.id,
                "starting_xi_count": len(starting_xi),
                "bench_count": len(bench_players),
                "starters_performance_created": starters_performance_created,
                "performance_updated": performance_count > 0,
                "performance_count": performance_count
            }
            
        except Exception as e:
            logger.error(f"Error submitting lineup: {str(e)}")
            raise

    @staticmethod
    def _validate_formation(formation: str, starting_xi: List[str]) -> bool:
        """
        Validate that the formation matches the player positions
        
        Args:
            formation: Formation string (e.g., '4-4-2')
            starting_xi: List of player IDs
            
        Returns:
            Boolean indicating if formation is valid
        """
        try:
            # formation_parts = formation.split('-')
            # if len(formation_parts) != 3:
            #     return False
            
            # expected_defenders = int(formation_parts[0])
            # expected_midfielders = int(formation_parts[1])
            # expected_forwards = int(formation_parts[2])
            
            # players = Player.objects.filter(id__in=starting_xi)
            # player_positions = [player.position for player in players]
            
            # actual_defenders = player_positions.count('DEF')
            # actual_midfielders = player_positions.count('MID')
            # actual_forwards = player_positions.count('FWD')
            # actual_goalkeepers = player_positions.count('GKP')
            
            # if actual_goalkeepers != 1:
            #     return False
            
            # if (actual_defenders != expected_defenders or 
            #     actual_midfielders != expected_midfielders or 
            #     actual_forwards != expected_forwards):
            #     return False
            
            return True
            
        except (ValueError, IndexError):
            return False

    @staticmethod
    def _create_starter_performances(players: List[Player], fixture: Fixture) -> int:
        """
        Create performance entries for starting players
        """
        created_count = 0
        gameweek = fixture.gameweek

        for player in players:
            existing_performance = PlayerPerformance.objects.filter(
                player=player, fixture=fixture
            ).first()

            if existing_performance:
                existing_performance.fantasy_points += 3
                existing_performance.minutes_played = max(
                    existing_performance.minutes_played or 0, 60
                )
                existing_performance.save()
                created_count += 1
                logger.info(
                    f"Updated existing performance for {player.name} with +3 starting points"
                )
            else:
                PlayerPerformance.objects.create(
                    player=player,
                    gameweek=gameweek,
                    fixture=fixture,
                    fantasy_points=3,
                    minutes_played=60,
                    yellow_cards=0,
                    red_cards=0,
                    goals_scored=0,
                    assists=0,
                    clean_sheets=0,
                    saves=0,
                    own_goals=0,
                    penalties_saved=0,
                    penalties_missed=0,
                )
                created_count += 1
                logger.info(
                    f"Created new performance for {player.name} with 3 starting points"
                )

        logger.info(
            f"Created/updated {created_count} starter performances for fixture {fixture.id}"
        )
        return created_count

    @staticmethod
    def get_team_players_for_fixture(team_id: str, fixture_id: str) -> List[Player]:
        """
        Get available players for a team that can be selected for a fixture
        
        Args:
            team_id: ID of the team
            fixture_id: ID of the fixture
            
        Returns:
            List of Player objects
        """
        try:
            team = get_object_or_404(Team, id=team_id)
            fixture = get_object_or_404(Fixture, id=fixture_id)
            
            players = Player.objects.filter(
                team=team,
                team__is_relegated=False
            ).order_by('position', 'jersey_number')
            
            return list(players)
            
        except Exception as e:
            logger.error(f"Error getting team players for fixture: {str(e)}")
            return []

    @staticmethod
    def get_existing_lineup(fixture_id: str, team_id: str) -> Optional[FixtureLineup]:
        """
        Get existing lineup for a fixture and team
        
        Args:
            fixture_id: ID of the fixture
            team_id: ID of the team
            
        Returns:
            FixtureLineup object or None if not found
        """
        try:
            lineup = FixtureLineup.objects.filter(
                fixture_id=fixture_id,
                team_id=team_id
            ).prefetch_related('players__player').first()
            
            return lineup
            
        except Exception as e:
            logger.error(f"Error getting existing lineup: {str(e)}")
            return None