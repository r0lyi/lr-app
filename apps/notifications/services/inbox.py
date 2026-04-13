"""Servicios de escritura para el inbox interno de notificaciones."""

from apps.notifications.models import Notification


def mark_notification_as_read(notification):
    """Marca una notificacion concreta como leida.

    La funcion es idempotente: si la notificacion ya estaba leida, no rompe ni
    genera escrituras innecesarias.
    """

    if notification.is_read:
        return notification

    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return notification


def mark_all_notifications_as_read(user):
    """Marca como leidas todas las notificaciones pendientes del usuario."""

    updated_count = Notification.objects.filter(
        user=user,
        is_read=False,
    ).update(is_read=True)
    return updated_count
