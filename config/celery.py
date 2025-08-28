"""
Celery configuration for the Django project.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from celery import Celery  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from typing import Any

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("config")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)  # type: ignore[misc]
def debug_task(self: Any) -> None:
    """Debug task for testing Celery setup."""
    return None
