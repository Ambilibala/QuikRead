from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import logging

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quikread.settings')
app = Celery('quikread')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

logger.info("Celery configured successfully.")
app.conf.worker_pool = 'solo'
