import logging
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone

from apps.kpl.models import TopcorerData, Gameweek, Player
from apps.kpl.tasks.fixtures import find_player

logger = logging.getLogger(__name__)

SCORERS_URL = "https://kenyafootballdata.com/tournament_scorers.php?t=uftn0043"


def parse_scorers_page(html_content: str) -> list[dict]:
    """
    Parse the Kenya Football Data scorers page to extract top 10 scorers.
    
    The page structure is:
    - Rank (number)
    - Player link
    - Team link
    - Goals (number immediately after team)
    
    Args:
        html_content: HTML content of the scorers page
        
    Returns:
        List of dictionaries containing player_name, team_name, goals, and rank
    """
    soup = BeautifulSoup(html_content, 'lxml')
    scorers = []
    
    # Get all text content split by lines
    text_content = soup.get_text()
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
    
    # Find all player and team links for reference
    all_links = soup.find_all('a', href=True)
    player_links = [link for link in all_links if 'player_goals.php' in link.get('href', '')]
    team_links = [link for link in all_links if 'team_goals.php' in link.get('href', '')]
    
    logger.info(f"Found {len(player_links)} player links and {len(team_links)} team links")
    
    # Build a mapping of player names to their teams and goals
    # The structure in the text is: Rank, Player, Team, Goals (repeating)
    import re
    
    # Create a list of player names and team names from links
    player_names = [link.get_text(strip=True) for link in player_links]
    team_names = [link.get_text(strip=True) for link in team_links]
    
    # Now parse the lines to find the pattern: rank, player, team, goals
    seen_players = set()
    i = 0
    
    while i < len(lines) and len(scorers) < 20:
        line = lines[i]
        
        # Check if this line is a rank number (1-100)
        if line.isdigit() and 1 <= int(line) <= 100:
            rank = int(line)
            
            # Next line should be player name
            if i + 1 < len(lines):
                potential_player = lines[i + 1]
                
                # Check if this is a known player name
                if potential_player in player_names and potential_player not in seen_players:
                    player_name = potential_player
                    seen_players.add(player_name)
                    
                    # Next line should be team name
                    if i + 2 < len(lines):
                        potential_team = lines[i + 2]
                        
                        # Check if this is a known team name
                        if potential_team in team_names:
                            team_name = potential_team
                            
                            # Next line should be goals
                            if i + 3 < len(lines):
                                potential_goals = lines[i + 3]
                                
                                # Check if it's a number (goals)
                                if potential_goals.isdigit():
                                    goals = int(potential_goals)
                                    
                                    scorers.append({
                                        'rank': rank,
                                        'player_name': player_name,
                                        'team_name': team_name,
                                        'goals': goals
                                    })
                                    
                                    logger.debug(f"Found scorer: {player_name} ({team_name}) - {goals} goals")
                                    i += 4  # Skip to next potential rank
                                    continue
        
        i += 1
    
    # If we didn't find enough scorers with the strict method, try a more lenient approach
    if len(scorers) < 10:
        logger.warning(f"Only found {len(scorers)} scorers with strict parsing, trying lenient approach")
        scorers = []
        seen_players = set()
        
        for idx, player_name in enumerate(player_names[:20]):
            if player_name in seen_players:
                continue
            seen_players.add(player_name)
            
            # Get corresponding team
            team_name = team_names[idx] if idx < len(team_names) else "Unknown"
            
            # Try to find goals by looking for numbers near this player in the text
            # Find the player's position in the text
            player_index = text_content.find(player_name)
            if player_index != -1:
                # Look at the text after the team name
                team_index = text_content.find(team_name, player_index)
                if team_index != -1:
                    # Extract a small chunk of text after the team name
                    chunk = text_content[team_index + len(team_name):team_index + len(team_name) + 50]
                    # Find the first number in this chunk
                    match = re.search(r'\b(\d+)\b', chunk)
                    goals = int(match.group(1)) if match else 0
                else:
                    goals = 0
            else:
                goals = 0
            
            scorers.append({
                'rank': idx + 1,
                'player_name': player_name,
                'team_name': team_name,
                'goals': goals
            })
    
    # Sort by goals descending and assign proper ranks
    scorers.sort(key=lambda x: x['goals'], reverse=True)
    
    # Assign ranks (handle ties)
    current_rank = 1
    for i, scorer in enumerate(scorers):
        if i > 0 and scorer['goals'] < scorers[i-1]['goals']:
            current_rank = i + 1
        scorer['rank'] = current_rank
    
    logger.info(f"Parsed {len(scorers)} scorers from page")
    
    # Return only top 10
    return scorers[:10]


@shared_task
def scrape_top_scorers(gameweek_id=None):
    """
    Scrape top 10 scorers from Kenya Football Data website.
    
    Args:
        gameweek_id: Optional gameweek ID. If not provided, uses the active gameweek.
        
    Returns:
        Dictionary with success status and count of scorers saved
    """
    try:
        # Get the gameweek
        if gameweek_id:
            gameweek = Gameweek.objects.get(id=gameweek_id)
        else:
            gameweek = Gameweek.objects.filter(is_active=True).first()
            
        if not gameweek:
            logger.error("No active gameweek found for scraping scorers")
            return {"success": False, "error": "No active gameweek found"}
        
        logger.info(f"Scraping top scorers for Gameweek {gameweek.number}")
        
        # Fetch the page
        response = requests.get(SCORERS_URL, timeout=30)
        response.raise_for_status()
        
        # Parse the scorers
        scorers = parse_scorers_page(response.text)
        
        if not scorers:
            logger.warning("No scorers found on the page")
            return {"success": False, "error": "No scorers found"}
        
        logger.info(f"Found {len(scorers)} scorers on the page")
        
        # Save to database
        saved_count = 0
        for scorer_data in scorers:
            # Try to match with existing player
            player = find_player(
                scorer_data['player_name'],
                team_name=scorer_data['team_name']
            )
            
            # Create or update the external scorer record
            external_scorer, created = TopcorerData.objects.update_or_create(
                gameweek=gameweek,
                player_name=scorer_data['player_name'],
                defaults={
                    'team_name': scorer_data['team_name'],
                    'goals': scorer_data['goals'],
                    'rank': scorer_data['rank'],
                    'player': player,
                }
            )
            
            saved_count += 1
            action = "Created" if created else "Updated"
            logger.info(
                f"{action} scorer: {scorer_data['player_name']} ({scorer_data['team_name']}) "
                f"- Rank {scorer_data['rank']}, {scorer_data['goals']} goals"
            )
            
            if not player:
                logger.warning(
                    f"Could not match player '{scorer_data['player_name']}' "
                    f"from team '{scorer_data['team_name']}' to database"
                )
        
        logger.info(f"Successfully saved {saved_count} scorers for Gameweek {gameweek.number}")
        return {
            "success": True,
            "gameweek": gameweek.number,
            "count": saved_count
        }
        
    except Gameweek.DoesNotExist:
        logger.error(f"Gameweek with ID {gameweek_id} not found")
        return {"success": False, "error": "Gameweek not found"}
    except requests.RequestException as e:
        logger.error(f"Error fetching scorers page: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error scraping scorers: {e}")
        return {"success": False, "error": str(e)}
