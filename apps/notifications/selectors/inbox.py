"""Selectores de lectura para el inbox interno de notificaciones.

La idea de este modulo es que las futuras vistas del inbox no tengan que
construir consultas a mano. Dejamos la lectura centralizada aqui para poder
añadir filtros o `select_related` sin tocar luego cada vista.
"""

from django.core.paginator import EmptyPage, Paginator

from apps.notifications.models import Notification


def get_user_inbox_notifications(user, *, is_read=None, limit=None):
    """Devuelve las notificaciones visibles para un usuario concreto.

    Parametros soportados:
    - `is_read=True/False`: filtra por leidas o no leidas
    - `limit`: recorta el numero de resultados utiles para widgets o previews

    La consulta incluye la solicitud asociada para que el inbox futuro pueda
    mostrar contexto sin disparar consultas adicionales por cada fila.
    """

    notifications = (
        Notification.objects.filter(user=user)
        .select_related(
            "created_by",
            "vacation_request",
            "vacation_request__employee",
            "vacation_request__status",
        )
        .order_by("-sent_at", "-id")
    )

    if is_read is not None:
        notifications = notifications.filter(is_read=is_read)

    if limit is not None:
        notifications = notifications[:limit]

    return notifications


def get_user_inbox_notifications_page(
    user,
    *,
    page_number=1,
    page_size=10,
    is_read=None,
):
    """Devuelve una pagina del inbox con tamano fijo.

    Para el dropdown del header elegimos paginas de 10 notificaciones, que es
    un tamano manejable para leer sin convertir el panel en una lista infinita.
    """

    notifications = get_user_inbox_notifications(user, is_read=is_read)
    paginator = Paginator(notifications, page_size)

    try:
        return paginator.page(page_number)
    except EmptyPage:
        return paginator.page(paginator.num_pages or 1)


def get_unread_notifications_count(user):
    """Cuenta cuantas notificaciones siguen sin leer para un usuario."""

    return Notification.objects.filter(user=user, is_read=False).count()


def get_user_inbox_notification_by_id(user, notification_id):
    """Obtiene una notificacion concreta del usuario propietario.

    Este helper evita accesos cruzados accidentales cuando mas adelante
    creemos acciones como "marcar como leida" o "ver detalle".
    """

    return (
        Notification.objects.filter(user=user)
        .select_related("created_by", "vacation_request")
        .get(pk=notification_id)
    )
