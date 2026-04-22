"""Servicios para avisos generales enviados por un administrador."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.notifications.models import Notification
from apps.notifications.selectors import get_admin_broadcast_notification_recipients


def create_admin_broadcast_notifications(*, sender, title, message):
    """Crea una notificación general para todos los usuarios activos."""

    normalized_title = (title or "").strip()
    normalized_message = (message or "").strip()

    if not normalized_title:
        raise ValidationError(_("El asunto del aviso general es obligatorio."))

    if not normalized_message:
        raise ValidationError(_("El mensaje del aviso general es obligatorio."))

    recipients = list(get_admin_broadcast_notification_recipients())
    if not recipients:
        return []

    notifications = [
        Notification(
            user=recipient,
            created_by=sender,
            notification_type=Notification.Type.ADMIN_BROADCAST_MESSAGE,
            title=normalized_title,
            message=normalized_message,
        )
        for recipient in recipients
    ]
    return Notification.objects.bulk_create(notifications)
