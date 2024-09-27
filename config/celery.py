from __future__ import absolute_import
import os
from celery import Celery
from config.settings import base

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("config")
app.config_from_object("config.settings.development", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: base.INSTALLED_APPS)