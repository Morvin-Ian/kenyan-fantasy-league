"""Remove the periodic tasks left behind by the per-fixture live monitor.

``apps.kpl.tasks.live_games`` created one ``PeriodicTask`` per fixture, pointing
at ``monitor_fixture_score``, and enabled it while the match was on. That module
is gone: a single scheduled task now reads every match on the page in one pass.

The rows outlive the code. django-celery-beat's DatabaseScheduler reads them on
startup and dispatching one raises ``NotRegistered``, so they are removed here
rather than left to fail every beat tick.
"""

from django.db import migrations

LIVE_GAMES_TASK = "apps.kpl.tasks.live_games.monitor_fixture_score"


def drop_orphaned_tasks(apps, schema_editor):
    try:
        PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    except LookupError:  # pragma: no cover - beat not installed
        return
    PeriodicTask.objects.filter(task=LIVE_GAMES_TASK).delete()
    # The scheduler names them per fixture; catch any that carry a different
    # task path but the same naming scheme.
    PeriodicTask.objects.filter(name__startswith="monitor_fixture_").delete()


def noop(apps, schema_editor):
    """Nothing to restore: the task these rows pointed at no longer exists."""


class Migration(migrations.Migration):

    dependencies = [
        ("kpl", "0023_player_position_source"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(drop_orphaned_tasks, noop),
    ]
