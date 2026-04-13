"""Servicios para avisar al empleado cuando RRHH cambia el estado."""

from apps.notifications.models import Notification


def build_vacation_status_changed_message(
    vacation_request,
    *,
    previous_status_name,
    new_status_name,
):
    """Construye un mensaje claro sobre el cambio de estado."""

    start_date = vacation_request.start_date.strftime("%d-%m-%Y")
    end_date = vacation_request.end_date.strftime("%d-%m-%Y")

    return (
        f"Tu solicitud de vacaciones del {start_date} al {end_date} ha cambiado "
        f"de estado: {previous_status_name} -> {new_status_name}."
    )


def create_vacation_status_changed_notification(
    vacation_request,
    *,
    previous_status_name,
    new_status_name,
):
    """Crea una notificacion solo si RRHH cambia realmente el estado."""

    normalized_previous = (previous_status_name or "").strip().lower()
    normalized_new = (new_status_name or "").strip().lower()

    if not normalized_previous or not normalized_new:
        return None

    if normalized_previous == normalized_new:
        return None

    return Notification.objects.create(
        user=vacation_request.employee.user,
        notification_type=Notification.Type.VACATION_REQUEST_STATUS,
        vacation_request=vacation_request,
        previous_status_name=normalized_previous,
        message=build_vacation_status_changed_message(
            vacation_request,
            previous_status_name=normalized_previous,
            new_status_name=normalized_new,
        ),
    )
