import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')

app = Celery('hello_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Do not execute all possible unprocessed cron tasks after long shutdown
# In other words, reset beat schedule onstartup
app.control.purge()

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.on_after_finalize.connect
def run_groups_update(sender, **kwargs):
    sender.send_task('groups.tasks.update_groups_members_count', args=(1, 100))
