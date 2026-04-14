"""Consultas de lectura usadas por el dominio de vacaciones."""

from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum

from apps.vacations.models import VacationRequest, VacationStatus
from apps.vacations.services.requests.policies import (
    ACTIVE_REQUEST_STATUS_NAMES,
    OPEN_REQUEST_STATUS_NAMES,
)


def get_vacation_status_by_name(status_name):
    """Devuelve el estado por nombre interno del catalogo de vacaciones."""
    return VacationStatus.objects.get(name=status_name)


def get_employee_vacation_requests(employee_profile):
    """Lista las solicitudes del empleado ordenadas de mas nueva a mas antigua."""
    return VacationRequest.objects.filter(
        employee=employee_profile,
    ).select_related("status").order_by("-request_date")


def get_filtered_employee_vacation_requests(
    employee_profile,
    *,
    start_date=None,
    end_date=None,
    status_name="",
):
    """Aplica los filtros del home del empleado sobre su lista de solicitudes.

    Los filtros son acumulativos y opcionales:
    - `start_date`: solo muestra solicitudes cuyo inicio sea igual o posterior
    - `end_date`: solo muestra solicitudes cuyo fin sea igual o anterior
    - `status_name`: solo muestra el estado seleccionado
    """
    requests_qs = get_employee_vacation_requests(employee_profile)

    if start_date is not None:
        requests_qs = requests_qs.filter(start_date__gte=start_date)

    if end_date is not None:
        requests_qs = requests_qs.filter(end_date__lte=end_date)

    normalized_status_name = (status_name or "").strip().lower()
    if normalized_status_name:
        requests_qs = requests_qs.filter(status__name=normalized_status_name)

    return requests_qs


def get_overlapping_active_requests(
    employee_profile,
    *,
    start_date,
    end_date,
    exclude_request_id=None,
):
    """Busca solapes con solicitudes que aun ocupan el mismo periodo.

    En esta fase tratamos como solicitudes activas las que estan pendientes o
    aprobadas, porque ambas bloquean el mismo rango de fechas.
    """
    requests_qs = VacationRequest.objects.filter(
        employee=employee_profile,
        status__name__in=ACTIVE_REQUEST_STATUS_NAMES,
        start_date__lte=end_date,
        end_date__gte=start_date,
    )

    if exclude_request_id is not None:
        requests_qs = requests_qs.exclude(pk=exclude_request_id)

    return requests_qs


def get_open_requests_for_employee(employee_profile, *, exclude_request_id=None):
    """Devuelve solicitudes aun abiertas para evitar duplicados pendientes."""

    requests_qs = VacationRequest.objects.filter(
        employee=employee_profile,
        status__name__in=OPEN_REQUEST_STATUS_NAMES,
    )

    if exclude_request_id is not None:
        requests_qs = requests_qs.exclude(pk=exclude_request_id)

    return requests_qs


def get_reserved_annual_vacation_days_for_year(employee_profile, *, year):
    """Suma los dias activos ya reservados para el ano indicado."""

    reserved_days = (
        VacationRequest.objects.filter(
            employee=employee_profile,
            status__name__in=ACTIVE_REQUEST_STATUS_NAMES,
            start_date__year=year,
        ).aggregate(total=Sum("requested_days"))["total"]
        or Decimal("0.00")
    )

    return Decimal(reserved_days).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
