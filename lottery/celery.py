import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery.settings')


app = Celery('mint')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()