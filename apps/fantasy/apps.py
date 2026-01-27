from django.apps import AppConfig


class FantasyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.fantasy"

    def ready(self):
        import apps.fantasy.signals  # noqa
