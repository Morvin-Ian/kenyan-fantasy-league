"""
Cache utilities for the Fantasy League application.

Provides centralized caching functions and decorators to improve performance
and ensure consistent cache key generation and invalidation.
"""

from django.core.cache import cache
from functools import wraps
import hashlib
import json
from typing import Any, Callable, List


def cache_key(*args, **kwargs) -> str:
    """
    Generate consistent cache keys from arguments.
    
    Args:
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        MD5 hash of the serialized arguments
    """
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def invalidate_fantasy_team_cache(team_id: str) -> None:
    """
    Invalidate all caches related to a fantasy team.
    
    Args:
        team_id: UUID of the fantasy team
    """
    cache.delete_many([
        f'fantasy_team_{team_id}',
        f'team_players_{team_id}',
        f'team_selections_{team_id}',
        f'user_team_{team_id}',
    ])


def invalidate_gameweek_cache(gameweek_number: int) -> None:
    """
    Invalidate gameweek-related caches.
    
    Args:
        gameweek_number: The gameweek number
    """
    cache.delete_many([
        f'gameweek_status_{gameweek_number}',
        f'gameweek_fixtures_{gameweek_number}',
        'active_gameweek_number',
        f'team_of_week_{gameweek_number}',
    ])


def invalidate_player_cache(player_id: str) -> None:
    """
    Invalidate player-related caches.
    
    Args:
        player_id: UUID of the player
    """
    cache.delete_many([
        f'player_{player_id}',
        f'player_performances_{player_id}',
        'goals_leaderboard',
        'players_list_*',  # Pattern - will need manual clearing
    ])


def cache_queryset(timeout: int = 300, key_prefix: str = '') -> Callable:
    """
    Decorator for caching queryset results.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for the cache key
        
    Returns:
        Decorated function that caches results
        
    Example:
        @cache_queryset(timeout=600, key_prefix='standings')
        def get_standings(gameweek):
            return Standing.objects.filter(gameweek=gameweek)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache_key_str = f"{key_prefix}:{cache_key(*args, **kwargs)}"
            result = cache.get(cache_key_str)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key_str, result, timeout)
            return result
        return wrapper
    return decorator


def get_or_set_cache(key: str, callback: Callable, timeout: int = 300) -> Any:
    """
    Get value from cache or set it using callback.
    
    Args:
        key: Cache key
        callback: Function to call if cache miss
        timeout: Cache timeout in seconds
        
    Returns:
        Cached or freshly computed value
        
    Example:
        active_gw = get_or_set_cache(
            'active_gameweek',
            lambda: Gameweek.objects.filter(is_active=True).first(),
            timeout=3600
        )
    """
    result = cache.get(key)
    if result is None:
        result = callback()
        cache.set(key, result, timeout)
    return result


def clear_pattern_cache(pattern: str) -> int:
    """
    Clear all cache keys matching a pattern.
    
    Note: This requires Redis as the cache backend.
    
    Args:
        pattern: Pattern to match (e.g., 'players_list_*')
        
    Returns:
        Number of keys deleted
    """
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        keys = conn.keys(pattern)
        if keys:
            return conn.delete(*keys)
        return 0
    except ImportError:
        # Fallback if django-redis is not available
        return 0
