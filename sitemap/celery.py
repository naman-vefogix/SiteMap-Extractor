import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sitemap.settings")

app = Celery("sitemap")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()