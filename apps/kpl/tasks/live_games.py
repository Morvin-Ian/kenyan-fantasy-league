import logging
import os
from datetime import timedelta

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

from apps.kpl.models import Fixture, Gameweek
from util.views import headers
from uuid import UUID
from config.settings import base

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)


def create_fixture_monitoring_task(fixture_id: UUID):
    """Create a periodic task to monitor a specific fixture's live score"""
    try:
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=5,
            period=IntervalSchedule.MINUTES,
        )
        
        task_name = f'monitor_fixture_{str(fixture_id)}'
        existing_task = PeriodicTask.objects.filter(name=task_name).first()
        
        if existing_task:
            # Update existing task to be enabled
            existing_task.enabled = True
            existing_task.save()
            logger.info(f"Enabled existing monitoring task for fixture {fixture_id}")
        else:
            # Create new monitoring task
            PeriodicTask.objects.create(
                interval=schedule,
                name=task_name,
                task='apps.kpl.tasks.live_games.monitor_fixture_score',
                args=json.dumps([str(fixture_id)]),
                enabled=True,
            )
            logger.info(f"Created new monitoring task for fixture {fixture_id}")
            
    except Exception as e:
        logger.error(f"Error creating monitoring task for fixture {fixture_id}: {e}")


def disable_fixture_monitoring_task(fixture_id: UUID):
    """Disable the monitoring task for a finished fixture"""
    try:
        task_name = f'monitor_fixture_{str(fixture_id)}'
        task = PeriodicTask.objects.filter(name=task_name).first()
        if task:
            task.enabled = False
            task.save()
            logger.info(f"Disabled monitoring task for fixture {fixture_id}")
    except Exception as e:
        logger.error(f"Error disabling monitoring task for fixture {fixture_id}: {e}")


def extract_live_score_data(fixture_url: str) -> dict:
    """Extract live score data from the fixture URL"""
    try:
        response = requests.get(fixture_url, headers=headers, verify=False, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to fetch live score. Status: {response.status_code}")
            return {}
            
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Look for common score elements
        score_data = {}
        
        # Try to find score elements - you'll need to adjust these selectors
        # based on the actual HTML structure of your live score page
        home_score_elem = soup.find('div', class_='home-score') or soup.find('span', class_='home-team-score')
        away_score_elem = soup.find('div', class_='away-score') or soup.find('span', class_='away-team-score')
        
        # Alternative: look for score pattern in text
        if not home_score_elem or not away_score_elem:
            # Try to find score pattern like "2 - 1" or "2:1"
            score_pattern = soup.find(text=lambda text: text and (' - ' in text or ':' in text) and any(char.isdigit() for char in text))
            if score_pattern:
                # Extract scores from pattern
                if ' - ' in score_pattern:
                    scores = score_pattern.strip().split(' - ')
                elif ':' in score_pattern:
                    scores = score_pattern.strip().split(':')
                else:
                    scores = []
                
                if len(scores) == 2 and scores[0].isdigit() and scores[1].isdigit():
                    score_data['home_score'] = int(scores[0])
                    score_data['away_score'] = int(scores[1])
        else:
            # Extract scores from specific elements
            if home_score_elem and home_score_elem.text.strip().isdigit():
                score_data['home_score'] = int(home_score_elem.text.strip())
            if away_score_elem and away_score_elem.text.strip().isdigit():
                score_data['away_score'] = int(away_score_elem.text.strip())
        
        # Check for match status indicators
        status_indicators = [
            soup.find('div', class_='match-status'),
            soup.find('span', class_='game-status'),
            soup.find(text=lambda text: text and any(status in text.lower() for status in ['live', 'completed', 'postponed']))
        ]
        
        for indicator in status_indicators:
            if indicator:
                status_text = indicator.text if hasattr(indicator, 'text') else str(indicator)
                status_lower = status_text.lower().strip()
                
                if any(word in status_lower for word in ['live', 'ongoing', 'in progress']):
                    score_data['match_status'] = 'live'
                    break
                elif any(word in status_lower for word in ['finished', 'full time', 'ft', 'final']):
                    score_data['match_status'] = 'completed'
                    break
        
        # If no explicit status found, infer from presence of scores
        if 'match_status' not in score_data and ('home_score' in score_data or 'away_score' in score_data):
            score_data['match_status'] = 'live'
            
        return score_data
        
    except requests.RequestException as e:
        logger.error(f"Network error fetching live score: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error extracting live score data: {e}")
        return {}


@shared_task
def monitor_fixture_score(fixture_id: UUID):
    """Monitor a specific fixture's live score every 5 minutes"""
    try:
        fixture = Fixture.objects.get(id=fixture_id)
        
        # Skip if fixture is already finished
        if fixture.status in ['completed', 'live', 'postponed']:
            disable_fixture_monitoring_task(fixture_id)
            return f"Fixture {fixture_id} already finished, monitoring disabled"
        
        current_time = timezone.now()
        match_time = fixture.match_date
        
        # Check if match should have started (with 5-minute buffer)
        if current_time < (match_time - timedelta(minutes=5)):
            return f"Fixture {fixture_id} hasn't started yet"
        
        # If match time has passed but status is still 'upcoming', check for live data
        if current_time >= match_time and fixture.status == 'upcoming':
            # Construct live score URL - adjust this based on your actual URL structure
            live_score_url = os.getenv('LIVE_SCORE_BASE_URL', 'https://example.com/live/')
            
            # You might need to construct the URL differently based on your site structure
            # For example: f"{base_url}/fixtures/{fixture.home_team.slug}-vs-{fixture.away_team.slug}"
            
            score_data = extract_live_score_data(live_score_url)
            
            if score_data:
                updated = False
                
                # Update scores if available
                if 'home_score' in score_data:
                    if fixture.home_score != score_data['home_score']:
                        fixture.home_score = score_data['home_score']
                        updated = True
                
                if 'away_score' in score_data:
                    if fixture.away_score != score_data['away_score']:
                        fixture.away_score = score_data['away_score']
                        updated = True
                
                # Update status
                if 'match_status' in score_data:
                    if score_data['match_status'] == 'live' and fixture.status != 'live':
                        fixture.status = 'live'
                        updated = True
                        logger.info(f"Fixture {fixture_id} status changed to ongoing")
                    
                    elif score_data['match_status'] == 'completed' and fixture.status != 'completed':
                        fixture.status = 'completed'
                        updated = True
                        disable_fixture_monitoring_task(fixture_id)
                        logger.info(f"Fixture {fixture_id} completed, monitoring disabled")
                
                if updated:
                    fixture.save()
                    return f"Updated fixture {fixture_id}: {fixture.home_team.name} {fixture.home_score or 0} - {fixture.away_score or 0} {fixture.away_team.name} ({fixture.status})"
                else:
                    return f"No updates needed for fixture {fixture_id}"
            else:
                # No live data available yet, but match time has passed
                if fixture.status == 'upcoming':
                    fixture.status = 'live'
                    fixture.save()
                    logger.info(f"Fixture {fixture_id} marked as ongoing (no live data yet)")
                return f"Fixture {fixture_id} marked as ongoing, waiting for live data"
        
        # Check if match should be finished (after 2.5 hours)
        if current_time > (match_time + timedelta(hours=2, minutes=30)) and fixture.status == 'ongoing':
            fixture.status = 'completed'
            fixture.save()
            disable_fixture_monitoring_task(fixture_id)
            logger.info(f"Fixture {fixture_id} auto-finished after 2.5 hours")
            return f"Auto-finished fixture {fixture_id} after 2.5 hours"
        
        return f"Monitoring fixture {fixture_id}, no updates needed"
        
    except Fixture.DoesNotExist:
        logger.error(f"Fixture {fixture_id} not found")
        disable_fixture_monitoring_task(fixture_id)
        return f"Fixture {fixture_id} not found, monitoring disabled"
    except Exception as e:
        logger.error(f"Error monitoring fixture {fixture_id}: {e}")
        return f"Error monitoring fixture {fixture_id}: {e}"




@shared_task
def setup_gameweek_monitoring():
    """Set up monitoring tasks for all upcoming fixtures in the active gameweek"""
    try:
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        if not active_gameweek:
            return "No active gameweek found"
        
        upcoming_fixtures = Fixture.objects.filter(
            gameweek=active_gameweek,
            status='upcoming'
        )
        
        tasks_created = 0
        for fixture in upcoming_fixtures:
            create_fixture_monitoring_task(fixture.id)
            tasks_created += 1
        
        logger.info(f"Set up monitoring for {tasks_created} fixtures in Gameweek {active_gameweek.number}")
        return f"Set up monitoring for {tasks_created} fixtures in Gameweek {active_gameweek.number}"
        
    except Exception as e:
        logger.error(f"Error setting up gameweek monitoring: {e}")
        return f"Error setting up gameweek monitoring: {e}"


@shared_task
def cleanup_finished_fixtures():
    """Clean up monitoring tasks for finished fixtures and update their status to 'past'"""
    try:
        # Find fixtures that are finished but not yet marked as 'past'
        finished_fixtures = Fixture.objects.filter(status='finished')
        updated_count = 0
        
        for fixture in finished_fixtures:
            # Update status to 'past' after a reasonable delay (e.g., 1 hour after match end)
            if fixture.match_date and timezone.now() > (fixture.match_date + timedelta(hours=3)):
                fixture.status = 'past'
                fixture.save()
                updated_count += 1
                
                # Ensure monitoring task is disabled
                disable_fixture_monitoring_task(fixture.id)
        
        logger.info(f"Updated {updated_count} fixtures from 'finished' to 'past'")
        return f"Updated {updated_count} fixtures from 'finished' to 'past'"
        
    except Exception as e:
        logger.error(f"Error cleaning up finished fixtures: {e}")
        return f"Error cleaning up finished fixtures: {e}"
