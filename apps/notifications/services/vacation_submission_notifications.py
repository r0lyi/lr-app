"""Servicios para avisar a RRHH de nuevas solicitudes de vacaciones."""

from apps.notifications.models import Notification
from apps.notifications.selectors import get_active_rrhh_notification_recipients


def build_vacation_submission_message(vacation_request):
    """Construye un mensaje claro para el inbox interno de RRHH.

    El texto resume quien ha enviado la solicitud y el rango pedido. Asi RRHH
    puede identificar la accion pendiente sin tener que abrir primero el detalle.
    """

    employee = vacation_request.employee
    employee_name = f"{employee.first_name} {employee.last_name}".strip()
    start_date = vacation_request.start_date.strftime("%d-%m-%Y")
    end_date = vacation_request.end_date.strftime("%d-%m-%Y")

    return (
        f"{employee_name} ha enviado una nueva solicitud de vacaciones "
        f"del {start_date} al {end_date}."
    )


def create_vacation_submission_notifications(vacation_request):
    """Crea una notificacion interna para cada destinatario de RRHH.

    La creacion se hace en el dominio `notifications` para que el flujo de
    vacaciones no tenga que conocer como se guardan ni a quien se avisa.
    """

    recipients = list(get_active_rrhh_notification_recipients())
    if not recipients:
        return []

    notification_message = build_vacation_submission_message(vacation_request)
    notifications = [
        Notification(
            user=recipient,
            notification_type=Notification.Type.VACATION_REQUEST_SUBMISSION,
            vacation_request=vacation_request,
            message=notification_message,
        )
        for recipient in recipients
    ]

    return Notification.objects.bulk_create(notifications)

