"""Servicios para notificaciones personales enviadas por administradores."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.notifications.models import Notification


def create_admin_personal_notification(*, sender, recipient, title, message):
    """Crea una notificación personal desde un administrador a un usuario.

    Se guarda dentro del inbox interno para mantener todo el historial de
    mensajes en el mismo sistema de notificaciones que ya usa la aplicación.
    """

    normalized_title = (title or "").strip()
    normalized_message = (message or "").strip()

    if not normalized_title:
        raise ValidationError(_("El asunto de la notificación es obligatorio."))

    if not normalized_message:
        raise ValidationError(_("El mensaje de la notificación es obligatorio."))

    return Notification.objects.create(
        user=recipient,
        created_by=sender,
        notification_type=Notification.Type.ADMIN_PERSONAL_MESSAGE,
        title=normalized_title,
        message=normalized_message,
    )
