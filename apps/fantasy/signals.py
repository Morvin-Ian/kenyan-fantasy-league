"""
Cache invalidation signals for the Fantasy app.

Automatically invalidates relevant caches when models are updated.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_redis import get_redis_connection
from apps.fantasy.models import TeamSelection, FantasyPlayer, FantasyTeam
from apps.kpl.models import Gameweek, FixtureLineup, TopcorerData


@receiver([post_save, post_delete], sender=TeamSelection)
def invalidate_team_selection_cache(sender, instance, **kwargs):
    """Invalidate caches when team selection is created/updated/deleted."""
    redis_conn = get_redis_connection("default")
    
    # Invalidate specific team selection cache
    keys_to_delete = [
        f"gameweek_selection_{instance.fantasy_team_id}_{instance.gameweek_id}",
        f"available_gameweeks_{instance.fantasy_team_id}",
        f"user_team_{instance.fantasy_team.user_id}_*",
    ]
    
    for key in keys_to_delete:
        if '*' in key:
            # Pattern-based deletion
            pattern_keys = redis_conn.keys(key)
            if pattern_keys:
                redis_conn.delete(*pattern_keys)
        else:
            redis_conn.delete(key)


@receiver(post_save, sender=Gameweek)
def invalidate_gameweek_cache(sender, instance, **kwargs):
    """Invalidate active gameweek cache when gameweek is updated."""
    if instance.is_active:
        redis_conn = get_redis_connection("default")
        redis_conn.delete("active_gameweek_number")
        
        # Also invalidate all available gameweeks caches
        pattern_keys = redis_conn.keys("available_gameweeks_*")
        if pattern_keys:
            redis_conn.delete(*pattern_keys)


@receiver([post_save, post_delete], sender=FixtureLineup)
def invalidate_lineup_cache(sender, instance, **kwargs):
    """Invalidate fixture lineup cache when lineup is updated."""
    redis_conn = get_redis_connection("default")
    redis_conn.delete(f"fixture_lineups_{instance.fixture_id}")


@receiver([post_save, post_delete], sender=TopcorerData)
def invalidate_leaderboard_cache(sender, instance, **kwargs):
    """Invalidate goals leaderboard cache when topscorer data is updated."""
    redis_conn = get_redis_connection("default")
    
    # Invalidate all leaderboard caches (different limits)
    pattern_keys = redis_conn.keys("goals_leaderboard_limit_*")
    if pattern_keys:
        redis_conn.delete(*pattern_keys)


@receiver([post_save, post_delete], sender=FantasyPlayer)
def invalidate_fantasy_player_cache(sender, instance, **kwargs):
    """Invalidate team players cache when fantasy player is updated."""
    redis_conn = get_redis_connection("default")
    
    keys_to_delete = [
        f"team_players_{instance.fantasy_team_id}",
        f"user_team_{instance.fantasy_team.user_id}_*",
    ]
    
    for key in keys_to_delete:
        if '*' in key:
            pattern_keys = redis_conn.keys(key)
            if pattern_keys:
                redis_conn.delete(*pattern_keys)
        else:
            redis_conn.delete(key)


@receiver([post_save, post_delete], sender=FantasyTeam)
def invalidate_fantasy_team_cache(sender, instance, **kwargs):
    """Invalidate fantasy team cache when team is updated."""
    redis_conn = get_redis_connection("default")
    
    # Invalidate user team caches
    pattern_keys = redis_conn.keys(f"user_team_{instance.user_id}_*")
    if pattern_keys:
        redis_conn.delete(*pattern_keys)
