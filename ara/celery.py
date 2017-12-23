
from __future__ import absolute_import, unicode_literals
import os

from django.conf import settings

from celery import Celery
from celery import task, shared_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ara.settings')
app = Celery('ara')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

CELERY_TIMEZONE = 'UTC'