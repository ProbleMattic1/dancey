import os
from celery import Celery

broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
backend_url = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/1')

celery = Celery('danceapp', broker=broker_url, backend=backend_url)
celery.conf.update(task_default_queue='default', task_serializer='json', result_serializer='json', accept_content=['json'])
