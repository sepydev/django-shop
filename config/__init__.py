# Config package

# Ensure Celery app is imported when Django starts so shared_task uses this app.
from .celery import app as celery_app

__all__ = ("celery_app",)
