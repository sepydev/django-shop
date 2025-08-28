# Celery and Timezone Configuration Guide

This document explains how to properly configure Celery and handle timezone changes in your Django scaffold project.

## Copier Configuration Variables

When generating or updating your project with Copier, you can control which services are included:

### Available Variables

- **`include_redis`** (boolean, default: true)
  - Include Redis service for caching and message broker
  - Required if you want to use Celery with Redis backend

- **`include_celery`** (boolean, default: true)
  - Include Celery worker for background task processing
  - Only available when `include_redis` is enabled

- **`include_celery_beat`** (boolean, default: true)
  - Include Celery Beat for periodic task scheduling
  - Only available when `include_celery` is enabled

### Usage

```bash
# Generate project with all services
copier copy . /path/to/new-project

# Generate project without Celery
copier copy . /path/to/new-project --data include_celery=false

# Generate project with Redis and Celery but no Beat
copier copy . /path/to/new-project --data include_celery_beat=false

# Update existing project
copier update
```

## Timezone Configuration

### Important Warning ⚠️

**If you change Django's `TIME_ZONE` setting after creating periodic tasks, you must reset the "last run time" for each periodic task.**

The periodic task schedule will still be based on the old timezone until you reset it.

### How to Reset Periodic Tasks

#### Method 1: Using Management Command (Recommended)

```bash
# Check what would be reset (dry run)
python manage.py reset_periodic_tasks --dry-run

# Reset all periodic tasks
python manage.py reset_periodic_tasks

# Reset without confirmation prompt
python manage.py reset_periodic_tasks --force
```

#### Method 2: Using Django Shell

```python
from django_celery_beat.models import PeriodicTask, PeriodicTasks

# Reset all periodic tasks
PeriodicTask.objects.all().update(last_run_at=None)
PeriodicTasks.update_changed()
```

### Configuration Best Practices

1. **Keep timezones aligned**: Ensure `CELERY_TIMEZONE` matches Django's `TIME_ZONE`
2. **Use UTC in production**: Recommended for consistent behavior across deployments
3. **Enable timezone awareness**: Always use `USE_TZ = True` in Django
4. **Reset after changes**: Always reset periodic tasks after timezone changes

### Current Configuration

The scaffold is configured with:

```python
# Django settings
TIME_ZONE = "UTC"
USE_TZ = True

# Celery settings (when enabled)
CELERY_TIMEZONE = TIME_ZONE  # Automatically synced
CELERY_ENABLE_UTC = True
```

## Docker Compose Services

The `docker-compose.yml` is generated conditionally based on your Copier choices:

### Service Dependencies

- **Redis**: Standalone service (when `include_redis=true`)
- **Celery Worker**: Depends on app, db, and redis (when `include_celery=true`)
- **Celery Beat**: Depends on app, db, redis, and celery worker (when `include_celery_beat=true`)

### Service Commands

```bash
# Start all services
docker-compose up

# Start only specific services
docker-compose up app db redis

# Scale celery workers
docker-compose up --scale celery=3

# View celery logs
docker-compose logs -f celery

# View celery beat logs
docker-compose logs -f celery-beat
```

## Utility Functions

The scaffold includes utility functions in `core.utils` to help manage timezone configuration:

```python
from core.utils import (
    check_timezone_configuration,
    validate_celery_timezone_config,
    TimezoneChangeHelper
)

# Check current configuration
config = check_timezone_configuration()
print(config)

# Validate Celery timezone settings
issues = validate_celery_timezone_config()
if issues:
    print("Configuration issues:", issues)

# Get reset instructions
instructions = TimezoneChangeHelper.get_reset_command_instructions()
print(instructions)
```

## Troubleshooting

### Common Issues

1. **Periodic tasks not running at expected times**
   - Check if you changed `TIME_ZONE` recently
   - Run `python manage.py reset_periodic_tasks`

2. **Celery can't connect to Redis**
   - Ensure Redis service is running: `docker-compose up redis`
   - Check `CELERY_BROKER_URL` environment variable

3. **Beat schedule not persisting**
   - Ensure `celery_beat_data` volume is mounted
   - Check database connectivity for Django Celery Beat

### Debugging Commands

```bash
# Check celery status
docker-compose exec celery celery -A config inspect active

# Check beat schedule
docker-compose exec celery-beat celery -A config beat --loglevel=debug

# Monitor task execution
docker-compose exec celery celery -A config events

# Purge all tasks
docker-compose exec celery celery -A config purge
```

## Migration Guide

If you're migrating from a project without this conditional setup:

1. Backup your current `docker-compose.yml`
2. Run `copier update` to regenerate with new template
3. Review and merge any custom changes
4. If you changed timezone settings, run `python manage.py reset_periodic_tasks`

## Environment Variables

Key environment variables you can customize:

```bash
# .env file
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

For production, consider using more robust message brokers and result backends.
