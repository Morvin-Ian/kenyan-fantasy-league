from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_redis import get_redis_connection

from apps.kpl.models import FixtureLineup, Gameweek, Player, Standing, TopcorerData


@receiver([post_save, post_delete], sender=Player)
def invalidate_player_cache(sender, instance, **kwargs):
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys("players_active_list_*")
    if keys:
        redis_conn.delete(*keys)


@receiver([post_save, post_delete], sender=Standing)
def invalidate_standing_cache(sender, instance, **kwargs):
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys("standings_list_page_*")
    if keys:
        redis_conn.delete(*keys)


@receiver([post_save, post_delete], sender=FixtureLineup)
def invalidate_fixture_lineup_cache(sender, instance, **kwargs):
    """Invalidate fixture lineup cache when lineup is updated."""
    redis_conn = get_redis_connection("default")
    redis_conn.delete(f"fixture_lineups_{instance.fixture_id}")


@receiver([post_save, post_delete], sender=TopcorerData)
def invalidate_topscorer_cache(sender, instance, **kwargs):
    """Invalidate goals leaderboard cache when topscorer data is updated."""
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys("goals_leaderboard_limit_*")
    if keys:
        redis_conn.delete(*keys)


@receiver(post_save, sender=Gameweek)
def invalidate_gameweek_cache_on_active_change(sender, instance, **kwargs):
    """Invalidate active gameweek cache when gameweek is activated."""
    if instance.is_active:
        redis_conn = get_redis_connection("default")
        redis_conn.delete("active_gameweek_number")
