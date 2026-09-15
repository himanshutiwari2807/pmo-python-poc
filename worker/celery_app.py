from celery import Celery

from app.config import settings

app = Celery("pmo_poc")
app.conf.update(
    broker_url=settings.redis_url,
    result_backend=settings.redis_url,
    task_serializer="json",
    accept_content=["json"],
    task_routes={"worker.tasks.*": {"queue": "analyze"}},
    worker_max_tasks_per_child=100,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

app.autodiscover_tasks(["worker"])
