import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("culinary_canvas")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


# Celery beat schedule (agar kerak bo'lsa)
app.conf.beat_schedule = {
    "publish-old-drafts": {
        "task": "dishes.tasks.publish_old_drafts_task",
        "schedule": 86400.0,  # Har 24 soatda
    },
}
app.conf.timezone = "Asia/Tashkent"
