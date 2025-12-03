"""
Django management command to test the scorers scraper
"""
from django.core.management.base import BaseCommand
from apps.kpl.tasks.scorers import scrape_top_scorers


class Command(BaseCommand):
    help = 'Test the top scorers scraper'

    def handle(self, *args, **options):
        self.stdout.write('Testing scorers scraper...')
        result = scrape_top_scorers()
        self.stdout.write(self.style.SUCCESS(f'Result: {result}'))
