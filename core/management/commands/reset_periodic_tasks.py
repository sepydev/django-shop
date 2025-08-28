"""
Django management command to reset periodic task schedules after timezone changes.

This command addresses the important warning about timezone changes in Celery Beat:
When you change Django's TIME_ZONE setting, periodic task schedules remain based
on the old timezone. This command resets all periodic tasks to fix this issue.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.management.base import BaseCommand
from django.db import transaction

if TYPE_CHECKING:
    from typing import Any

    from django.core.management.base import CommandParser


class Command(BaseCommand):
    help = """
    Reset periodic task schedules after timezone changes.

    IMPORTANT: This command should be run after changing Django's TIME_ZONE setting.
    It will reset the 'last_run_at' field for all periodic tasks, effectively treating
    them as if they have never run before.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be reset without making changes",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Skip confirmation prompt",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            from django_celery_beat.models import PeriodicTask  # type: ignore[import-untyped]
            from django_celery_beat.models import PeriodicTasks
        except ImportError:
            self.stdout.write(
                self.style.ERROR("django-celery-beat is not installed. Install it with: pip install django-celery-beat")
            )
            return

        # Get all periodic tasks
        tasks = PeriodicTask.objects.all()
        task_count = tasks.count()

        if task_count == 0:
            self.stdout.write(self.style.WARNING("No periodic tasks found."))
            return

        # Show what will be affected
        self.stdout.write(f"Found {task_count} periodic task(s):")
        for task in tasks:
            last_run = task.last_run_at.strftime("%Y-%m-%d %H:%M:%S UTC") if task.last_run_at else "Never"
            self.stdout.write(f"  - {task.name} (last run: {last_run})")

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS("\nDRY RUN: Would reset last_run_at for all tasks above."))
            return

        # Confirmation prompt
        if not options["force"]:
            self.stdout.write(self.style.WARNING("\nThis will reset the 'last_run_at' field for all periodic tasks."))
            self.stdout.write("Tasks will be treated as if they have never run before.")

            confirm = input("Are you sure you want to continue? [y/N]: ")
            if confirm.lower() not in ["y", "yes"]:
                self.stdout.write("Operation cancelled.")
                return

        # Perform the reset
        try:
            with transaction.atomic():
                updated_count = PeriodicTask.objects.all().update(last_run_at=None)
                PeriodicTasks.update_changed()

                self.stdout.write(self.style.SUCCESS(f"Successfully reset {updated_count} periodic task(s)."))
                self.stdout.write("PeriodicTasks.update_changed() has been called to refresh the scheduler.")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error resetting periodic tasks: {e}"))
            raise
