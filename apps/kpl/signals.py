from django_redis import get_redis_connection
from apps.kpl.models import Player, Standing
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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