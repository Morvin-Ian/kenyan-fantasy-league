from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser if one does not exist'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Superuser email')
        parser.add_argument('--username', type=str, help='Superuser username')
        parser.add_argument('--password', type=str, help='Superuser password')

    def handle(self, *args, **options):
        email = options.get('email') or 'admin@kpl-fantasy.com'
        username = options.get('username') or 'admin'
        password = options.get('password') or 'admin123'

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser with email {email} already exists')
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser with username {username} already exists')
            )
            return

        with transaction.atomic():
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )

        self.stdout.write(
            self.style.SUCCESS(f'Superuser created successfully: {email}')
        )
        self.stdout.write(f'Password: {password}')
