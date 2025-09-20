# Create this file: apps/kpl/management/commands/test_monitoring.py

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from apps.kpl.models import Fixture, Gameweek
from apps.kpl.tasks.live_games import setup_gameweek_monitoring, monitor_fixture_score
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test fixture monitoring setup'

    def add_arguments(self, parser):
        parser.add_argument('--setup', action='store_true', help='Setup monitoring tasks')
        parser.add_argument('--list', action='store_true', help='List all monitoring tasks')
        parser.add_argument('--test-fixture', type=str, help='Test specific fixture by ID')
        parser.add_argument('--cleanup', action='store_true', help='Clean up all monitoring tasks')

    def handle(self, *args, **options):
        if options['setup']:
            self.stdout.write('Setting up gameweek monitoring...')
            result = setup_gameweek_monitoring()
            self.stdout.write(self.style.SUCCESS(result))
            
        elif options['list']:
            self.list_monitoring_tasks()
            
        elif options['test_fixture']:
            fixture_id = options['test_fixture']
            self.stdout.write(f'Testing fixture monitoring for {fixture_id}...')
            result = monitor_fixture_score(fixture_id)
            self.stdout.write(self.style.SUCCESS(result))
            
        elif options['cleanup']:
            self.cleanup_tasks()
            
        else:
            self.show_status()

    def list_monitoring_tasks(self):
        tasks = PeriodicTask.objects.filter(name__startswith='monitor_fixture_')
        self.stdout.write(f'Found {tasks.count()} monitoring tasks:')
        for task in tasks:
            status = 'ENABLED' if task.enabled else 'DISABLED'
            self.stdout.write(f'  - {task.name}: {status} (Last run: {task.last_run_at})')

    def cleanup_tasks(self):
        count = PeriodicTask.objects.filter(name__startswith='monitor_fixture_').count()
        PeriodicTask.objects.filter(name__startswith='monitor_fixture_').delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} monitoring tasks'))

    def show_status(self):
        # Show active gameweek
        active_gameweek = Gameweek.objects.filter(is_active=True).first()
        if active_gameweek:
            self.stdout.write(f'Active gameweek: {active_gameweek.number}')
            
            fixtures = Fixture.objects.filter(
                gameweek=active_gameweek,
                status__in=['upcoming', 'live']
            )
            self.stdout.write(f'Fixtures in active gameweek: {fixtures.count()}')
            
            for fixture in fixtures:
                self.stdout.write(f'  - {fixture.home_team} vs {fixture.away_team} ({fixture.status})')
        else:
            self.stdout.write('No active gameweek found')
        
        # Show monitoring tasks
        self.list_monitoring_tasks()
        
        # Show Selenium connectivity
        try:
            from apps.kpl.tasks.live_games import get_selenium_driver
            driver = get_selenium_driver()
            driver.quit()
            self.stdout.write(self.style.SUCCESS('Selenium connection: OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Selenium connection failed: {e}'))