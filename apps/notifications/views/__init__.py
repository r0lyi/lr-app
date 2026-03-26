"""Exportaciones publicas de vistas del dominio de notificaciones."""

from .view_inbox_actions import (
    mark_all_notifications_as_read_view,
    mark_notification_as_read_view,
)

__all__ = [
    "mark_all_notifications_as_read_view",
    "mark_notification_as_read_view",
]
