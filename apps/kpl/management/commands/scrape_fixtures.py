from django.core.management.base import BaseCommand
from apps.kpl.tasks.live_games import monitor_fixture_score


class Command(BaseCommand):
    help = 'Scrape fixtures for a specific date'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to scrape (e.g., "25 OCT", "TODAY")',
            default=None
        )
        parser.add_argument(
            '--fixture-id',
            type=str,
            help='Specific fixture ID to monitor',
            default=None
        )

    def handle(self, *args, **options):
        target_date = options['date']
        fixture_id = options['fixture_id']
        
        if target_date:
            self.stdout.write(
                self.style.WARNING(f'Starting fixture scraping for date: {target_date}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Starting fixture scraping for default date (TODAY)')
            )
        
        # Call the task directly (not as a Celery task)
        result = monitor_fixture_score(fixture_id=fixture_id, target_date=target_date)
        
        if result:
            self.stdout.write(self.style.SUCCESS('Successfully scraped fixtures'))
        else:
            self.stdout.write(self.style.ERROR('Failed to scrape fixtures'))