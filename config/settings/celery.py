from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from .base import TIME_ZONE
from .base import env

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from typing import Any

# Celery Configuration
# ===================

# Redis-based broker and result backend
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")  # type: ignore[has-type]
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/0")  # type: ignore[has-type]
# Serialization settings
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Timezone Configuration
# =====================
# IMPORTANT: CELERY_TIMEZONE should match Django's TIME_ZONE setting
# If you change TIME_ZONE after creating periodic tasks, you must reset them:
#   python manage.py reset_periodic_tasks
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Celery Beat (Periodic Tasks) Configuration
# ==========================================
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Optional: Configure beat schedule file location
# CELERY_BEAT_SCHEDULE_FILENAME = "celerybeat-schedule"
# Task execution settings
CELERY_RESULT_EXPIRES = 3600
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True

# Task routing configuration
CELERY_TASK_ROUTES: dict[str, Any] = {
    # Example: Route specific tasks to specific queues
    # 'myapp.tasks.heavy_task': {'queue': 'heavy'},
    # 'myapp.tasks.light_task': {'queue': 'light'},
}

# Optional: Task retry configuration
CELERY_TASK_RETRY_DELAY = 60  # seconds
CELERY_TASK_MAX_RETRIES = 3

# Optional: Worker configuration
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
CELERY_WORKER_TASK_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s"

# Security settings
CELERY_TASK_REJECT_ON_WORKER_LOST = True

# Timezone change warning for development


def _log_timezone_warning() -> None:
    """Log timezone configuration warning during settings import."""
    logger.warning(
        "Celery Beat is enabled. If you change TIME_ZONE setting, "
        "run 'python manage.py reset_periodic_tasks' to reset task schedules."
    )


# Only log in development to avoid spamming production logs

if os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith("development"):
    _log_timezone_warning()
