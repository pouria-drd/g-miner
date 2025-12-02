from celery import Celery
from celery.schedules import crontab

from .settings import get_settings

settings_data = get_settings()

SCHEDULER_INTERVAL_MINUTES = int(settings_data["SCHEDULER_INTERVAL_MINUTES"])

celery_app = Celery(
    settings_data["PROJECT_NAME"],
    broker=settings_data["BROKER_URL"],
    backend=settings_data["RESULT_BACKEND"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


celery_app.autodiscover_tasks(
    [
        "modules.tasks",
    ],
)

celery_app.conf.beat_schedule = {
    f"run-gold-every-{SCHEDULER_INTERVAL_MINUTES}-minutes": {
        "task": "modules.tasks.gold_tasks.fetch_and_send",
        "schedule": crontab(minute=f"*/{SCHEDULER_INTERVAL_MINUTES}"),
    },
}
