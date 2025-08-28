from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.http import HttpResponse

logger = logging.getLogger(__name__)


class CustomMiddleware(MiddlewareMixin):
    """
    Custom middleware for request processing.
    """

    def process_request(self, request: HttpRequest) -> None:
        """
        Process the request before it reaches the view.
        """
        request.start_time = time.time()  # type: ignore[attr-defined]
        return None

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Process the response before it's sent to the client.
        """
        # Add custom headers

        # Log request duration
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")

        return response


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware to handle API versioning.
    """

    def process_request(self, request: HttpRequest) -> None:
        """
        Add API version to request.
        """
        if request.path.startswith("/api/"):
            version = request.META.get("HTTP_API_VERSION", "v1")
            request.api_version = version  # type: ignore[attr-defined]
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to responses.
    """

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Add security headers.
        """
        if not settings.DEBUG:
            response["X-Content-Type-Options"] = "nosniff"
            response["X-Frame-Options"] = "DENY"
            response["X-XSS-Protection"] = "1; mode=block"
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
