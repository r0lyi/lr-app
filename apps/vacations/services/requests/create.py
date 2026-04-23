"""Caso de uso para registrar una solicitud de vacaciones."""

from apps.notifications.services import (
    create_vacation_submission_notifications,
)
from apps.vacations.models import VacationRequest
from apps.vacations.selectors.request_queries import get_vacation_status_by_name

from .policies import DEFAULT_NEW_REQUEST_STATUS_NAME
from .validators import validate_employee_vacation_request


def create_employee_vacation_request(
    employee_profile,
    *,
    start_date,
    end_date,
    employee_comment="",
):
    """Crea una solicitud en estado pending tras validar el rango pedido.

    El caso de uso delega toda la validacion previa al modulo `validators`
    para que las reglas sean reutilizables y no queden mezcladas con la
    escritura final del modelo.
    """
    requested_days = validate_employee_vacation_request(
        employee_profile,
        start_date=start_date,
        end_date=end_date,
    )

    pending_status = get_vacation_status_by_name(DEFAULT_NEW_REQUEST_STATUS_NAME)

    vacation_request = VacationRequest.objects.create(
        employee=employee_profile,
        status=pending_status,
        start_date=start_date,
        end_date=end_date,
        requested_days=requested_days,
        employee_comment=employee_comment.strip() or None,
    )

    # Una vez creada la solicitud, avisamos al inbox interno de RRHH para que
    # aparezca pendiente de revision en su flujo de trabajo.
    create_vacation_submission_notifications(vacation_request)

    return vacation_request
