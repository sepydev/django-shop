"""
Core utility functions for the Django scaffold project.
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def check_timezone_configuration() -> dict[str, str]:
    """
    Check the current timezone configuration and return recommendations.

    Returns:
        Dict with timezone info and recommendations.
    """
    result = {
        "django_timezone": settings.TIME_ZONE,
        "use_tz": str(settings.USE_TZ),
        "celery_timezone": getattr(settings, "CELERY_TIMEZONE", "Not set"),
        "celery_enable_utc": str(getattr(settings, "CELERY_ENABLE_UTC", "Not set")),
    }

    # Add recommendations
    recommendations = []

    if not settings.USE_TZ:
        recommendations.append("Enable USE_TZ=True for timezone-aware datetime handling")

    if hasattr(settings, "CELERY_TIMEZONE") and settings.CELERY_TIMEZONE != settings.TIME_ZONE:
        recommendations.append(
            f"CELERY_TIMEZONE ({settings.CELERY_TIMEZONE}) differs from "
            f"TIME_ZONE ({settings.TIME_ZONE}). Consider aligning them."
        )

    if hasattr(settings, "CELERY_ENABLE_UTC") and not settings.CELERY_ENABLE_UTC and settings.TIME_ZONE != "UTC":
        recommendations.append("Consider enabling CELERY_ENABLE_UTC=True for better timezone handling")

    result["recommendations"] = recommendations
    return result


def log_timezone_warning() -> None:
    """
    Log a warning about timezone changes and periodic tasks.

    This should be called during application startup if django-celery-beat is installed.
    """
    try:
        import django_celery_beat  # type: ignore[import-untyped]  # noqa: F401

        logger.warning(
            "TIMEZONE CONFIGURATION WARNING: "
            "If you change Django's TIME_ZONE setting after creating periodic tasks, "
            "you must reset the 'last_run_at' field for each task. "
            "Run: python manage.py reset_periodic_tasks"
        )
    except ImportError:
        # django-celery-beat not installed, skip warning
        pass


def validate_celery_timezone_config() -> list[str]:
    """
    Validate Celery timezone configuration and return any issues found.

    Returns:
        List of configuration issues (empty if all good).
    """
    issues: list[str] = []

    # Check if Celery is configured
    if not hasattr(settings, "CELERY_BROKER_URL"):
        return issues  # Celery not configured, skip validation

    # Check timezone alignment
    django_tz = settings.TIME_ZONE
    celery_tz = getattr(settings, "CELERY_TIMEZONE", None)
    celery_utc = getattr(settings, "CELERY_ENABLE_UTC", None)

    if celery_tz is None:
        issues.append("CELERY_TIMEZONE is not set")
    elif celery_tz != django_tz:
        issues.append(f"CELERY_TIMEZONE ({celery_tz}) should match TIME_ZONE ({django_tz})")

    if celery_utc is None:
        issues.append("CELERY_ENABLE_UTC is not set")
    elif not celery_utc and django_tz != "UTC":
        issues.append("Consider setting CELERY_ENABLE_UTC=True when TIME_ZONE is not UTC")

    return issues


class TimezoneChangeHelper:
    """
    Helper class for managing timezone changes safely.
    """

    @staticmethod
    def get_reset_command_instructions() -> str:
        """
        Get instructions for resetting periodic tasks after timezone change.
        """
        return """
After changing Django's TIME_ZONE setting, run:

    python manage.py reset_periodic_tasks

Or manually in Django shell:
    from django_celery_beat.models import PeriodicTask, PeriodicTasks
    PeriodicTask.objects.all().update(last_run_at=None)
    PeriodicTasks.update_changed()

This resets all periodic tasks as if they've never run before.
        """.strip()

    @staticmethod
    def check_periodic_tasks_need_reset() -> str | None:
        """
        Check if periodic tasks might need reset due to timezone changes.

        Returns:
            Warning message if tasks might need reset, None otherwise.
        """
        try:
            from django_celery_beat.models import PeriodicTask  # type: ignore[import-untyped]

            # This is a simple heuristic - in a real app you might store
            # the last known timezone and compare it
            tasks_with_runs = PeriodicTask.objects.filter(last_run_at__isnull=False)

            if tasks_with_runs.exists():
                return (
                    f"Found {tasks_with_runs.count()} periodic task(s) with run history. "
                    "If you recently changed TIME_ZONE, consider running: "
                    "python manage.py reset_periodic_tasks"
                )
        except ImportError:
            # django-celery-beat not installed
            pass

        return None
