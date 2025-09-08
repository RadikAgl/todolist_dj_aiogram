import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todolist_dj_aiogram.settings')

app = Celery('todolist_dj_aiopgram')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.imports = ['tdlist_api.tasks']

app.conf.beat_schedule = {
    'every': {
        'task': 'tdlist_api.tasks.get_hot_tasks',
        'schedule': crontab(),
    },
}
