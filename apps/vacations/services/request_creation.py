"""Reglas de negocio para crear solicitudes de vacaciones del empleado."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.notifications.services import (
    create_vacation_submission_notifications,
)
from apps.vacations.models import VacationRequest
from apps.vacations.services.policies import (
    DEFAULT_NEW_REQUEST_STATUS_NAME,
    MAX_REQUESTED_VACATION_DAYS,
    MIN_ADVANCE_NOTICE_DAYS,
    MIN_REQUESTED_VACATION_DAYS,
    VACATION_DAY_COUNT_MODE,
)
from apps.vacations.selectors.request_queries import (
    get_open_requests_for_employee,
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


def get_request_annual_entitlement(employee_profile, *, year):
    """Calcula el derecho anual aplicable al ano del inicio solicitado."""

    from apps.employees.services.employee_dashboard import (
        calculate_annual_vacation_days_for_year,
    )

    return calculate_annual_vacation_days_for_year(
        employee_profile.hire_date,
        year=year,
    )


def validate_employee_vacation_request(
    employee_profile,
    *,
    start_date,
    end_date,
):
    """Valida las reglas de negocio previas al alta de una solicitud."""

    validation_errors = []

    if end_date < start_date:
        validation_errors.append(
            "La fecha de fin no puede ser anterior a la fecha de inicio."
        )

    if VACATION_DAY_COUNT_MODE != "natural":
        validation_errors.append(
            "El modo de conteo de dias configurado no esta soportado todavia."
        )

    today = timezone.localdate()
    if start_date < today:
        validation_errors.append(
            "La fecha de inicio no puede estar en el pasado."
        )
    elif (start_date - today).days < MIN_ADVANCE_NOTICE_DAYS:
        validation_errors.append(
            "La fecha de inicio debe solicitarse con al menos 30 dias naturales de antelacion."
        )

    if validation_errors:
        raise ValidationError(validation_errors)

    requested_days = calculate_requested_natural_days(start_date, end_date)
    if (
        requested_days < MIN_REQUESTED_VACATION_DAYS
        or requested_days > MAX_REQUESTED_VACATION_DAYS
    ):
        validation_errors.append(
            "La solicitud debe incluir entre 3 y 30 dias naturales."
        )

    annual_entitlement = get_request_annual_entitlement(
        employee_profile,
        year=start_date.year,
    )
    if requested_days > annual_entitlement:
        validation_errors.append(
            f"Los dias solicitados superan el derecho anual disponible para {start_date.year}."
        )

    if get_open_requests_for_employee(employee_profile).exists():
        validation_errors.append(
            "Ya existe una solicitud pendiente. Debe resolverse antes de registrar una nueva."
        )

    overlapping_requests = get_overlapping_active_requests(
        employee_profile,
        start_date=start_date,
        end_date=end_date,
    )
    if overlapping_requests.exists():
        validation_errors.append(
            "Ya existe una solicitud pendiente o aprobada que se solapa con ese periodo."
        )

    if validation_errors:
        raise ValidationError(validation_errors)

    return requested_days


def create_employee_vacation_request(
    employee_profile,
    *,
    start_date,
    end_date,
    employee_comment="",
):
    """Crea una solicitud en estado pending tras validar el rango pedido.

    Reglas aplicadas en esta fase:
    - la fecha de fin no puede ser anterior al inicio
    - la fecha de inicio no puede estar en el pasado
    - exigimos al menos 30 dias naturales de preaviso
    - solo aceptamos solicitudes de 3 a 30 dias naturales
    - los dias pedidos no pueden superar el derecho anual del ejercicio
    - no permitimos otra solicitud pendiente abierta del mismo empleado
    - no permitimos solapar periodos con solicitudes pendientes o aprobadas
    - toda solicitud nueva nace en estado pending
    - requested_days se calcula automaticamente a partir del rango
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
