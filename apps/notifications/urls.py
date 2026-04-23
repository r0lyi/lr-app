"""URLs del dominio de notificaciones."""

from django.urls import path

from apps.notifications.views import (
    mark_all_notifications_as_read_view,
    mark_notification_as_read_view,
)

app_name = "notifications"

urlpatterns = [
    path(
        "read-all/",
        mark_all_notifications_as_read_view,
        name="mark-all-read",
    ),
    path(
        "<int:notification_id>/read/",
        mark_notification_as_read_view,
        name="mark-read",
    ),
]
