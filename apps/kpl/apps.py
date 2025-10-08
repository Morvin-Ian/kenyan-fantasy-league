from django.apps import AppConfig


class KplConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.kpl"

    def ready(self):
        import apps.kpl.signals