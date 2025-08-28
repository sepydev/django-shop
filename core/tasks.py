"""
Example Celery tasks for the Django project.

This file demonstrates how to create Celery tasks that can be scheduled with Celery Beat.
"""

import logging

from celery import shared_task  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


@shared_task  # type: ignore[misc]
def test_task() -> str:
    """
    A simple test task to verify Celery is working.
    """
    logger.info("Test task executed")
    return "Test task completed successfully"
