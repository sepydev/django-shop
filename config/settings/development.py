"""
Django development settings for django-scaffold project.
"""

from .base import *  # noqa: F403
from .base import INSTALLED_APPS
from .base import MIDDLEWARE

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]


# Development-specific apps
INSTALLED_APPS.extend(
    [
        "django_extensions",
        "debug_toolbar",
    ]
)

# Development middleware
MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

# Debug toolbar configuration
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache (dummy cache for development)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Django Extensions
SHELL_PLUS_PRINT_SQL = True
