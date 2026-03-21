"""Reglas de negocio para crear solicitudes de vacaciones del empleado."""

from decimal import Decimal

from django.core.exceptions import ValidationError

from apps.vacations.models import VacationRequest
from apps.vacations.policies import (
    DEFAULT_NEW_REQUEST_STATUS_NAME,
    VACATION_DAY_COUNT_MODE,
)
from apps.vacations.selectors.request_queries import (
    get_overlapping_active_requests,
    get_vacation_status_by_name,
)


def calculate_requested_natural_days(start_date, end_date):
    """Calcula los dias naturales incluidos en el rango seleccionado.

    El conteo es inclusivo:
    - del 1 al 1 son 1 dia
    - del 1 al 5 son 5 dias

    Usamos dias naturales porque toda la logica actual del proyecto esta
    siguiendo la politica central definida para este sistema.
    """
    return Decimal((end_date - start_date).days + 1).quantize(Decimal("0.00"))


def create_employee_vacation_request(
    employee_profile,
    *,
    start_date,
    end_date,
    employee_comment="",
):
    """Crea una solicitud en estado pending tras validar el rango pedido.

    Reglas aplicadas en esta primera version:
    - la fecha de fin no puede ser anterior al inicio
    - no permitimos solapar periodos con solicitudes pendientes o aprobadas
    - toda solicitud nueva nace en estado pending
    - requested_days se calcula automaticamente a partir del rango
    """
    if end_date < start_date:
        raise ValidationError(
            "La fecha de fin no puede ser anterior a la fecha de inicio."
        )

    overlapping_requests = get_overlapping_active_requests(
        employee_profile,
        start_date=start_date,
        end_date=end_date,
    )
    if overlapping_requests.exists():
        raise ValidationError(
            "Ya existe una solicitud pendiente o aprobada que se solapa con ese periodo."
        )

    if VACATION_DAY_COUNT_MODE != "natural":
        raise ValidationError(
            "El modo de conteo de dias configurado no esta soportado todavia."
        )

    pending_status = get_vacation_status_by_name(DEFAULT_NEW_REQUEST_STATUS_NAME)

    return VacationRequest.objects.create(
        employee=employee_profile,
        status=pending_status,
        start_date=start_date,
        end_date=end_date,
        requested_days=calculate_requested_natural_days(start_date, end_date),
        employee_comment=employee_comment.strip() or None,
    )
