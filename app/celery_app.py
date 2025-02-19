# app/celery_app.py

from celery import Celery
from app.config import settings

# Example, let's say we're using Redis broker:
# settings.redis_url might look like 'redis://localhost:6379/0'
celery_app = Celery(
    "zance",
    broker=settings.redis_url,
    backend=settings.redis_url,  # optional, if you want to store results
)

# Celery config can go here
celery_app.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
