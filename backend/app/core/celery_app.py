from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configure periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "check-alerts-every-hour": {
        "task": "app.tasks.monitoring_tasks.check_all_alerts",
        "schedule": 3600.0,  # Run every hour
    },
}
