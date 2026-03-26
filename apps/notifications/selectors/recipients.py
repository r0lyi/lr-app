"""Consultas para resolver destinatarios de notificaciones internas."""

from apps.users.models import User


def get_active_rrhh_notification_recipients():
    """Devuelve los usuarios activos que actualmente trabajan como RRHH.

    En esta primera iteracion, cuando un empleado envia una solicitud de
    vacaciones, avisamos a todos los usuarios con rol `rrhh`. Dejamos la
    consulta en un selector para no mezclar reglas de destinatarios dentro
    de los servicios de negocio.
    """

    return User.objects.filter(
        is_active=True,
        roles__name="rrhh",
    ).distinct()

