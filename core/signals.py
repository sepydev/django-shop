from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.core.management.color import no_style
from django.db import connection
from django.db.models.signals import post_migrate
from django.dispatch import receiver

if TYPE_CHECKING:
    from typing import Any

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_migrate)
def reset_sequences(sender: Any, **kwargs: Any) -> None:
    """
    Reset database sequences after loading fixtures.
    """
    if connection.vendor == "postgresql":
        try:
            style = no_style()
            sql = connection.ops.sql_flush(style, [sender._meta.db_table])
            if sql:
                with connection.cursor() as cursor:
                    for query in sql:
                        cursor.execute(query)
        except Exception as e:
            logger.error(f"Failed to reset sequences: {e}")
