"""Consultas de lectura usadas por el dominio de vacaciones."""

from apps.vacations.models import VacationRequest, VacationStatus
from apps.vacations.services.policies import ACTIVE_REQUEST_STATUS_NAMES


def get_vacation_status_by_name(status_name):
    """Devuelve el estado por nombre interno del catalogo de vacaciones."""
    return VacationStatus.objects.get(name=status_name)


def get_employee_vacation_requests(employee_profile):
    """Lista las solicitudes del empleado ordenadas de mas nueva a mas antigua."""
    return VacationRequest.objects.filter(
        employee=employee_profile,
    ).select_related("status").order_by("-request_date")


def get_overlapping_active_requests(employee_profile, *, start_date, end_date):
    """Busca solapes con solicitudes que aun ocupan el mismo periodo.

    En esta fase tratamos como solicitudes activas las que estan pendientes o
    aprobadas, porque ambas bloquean el mismo rango de fechas.
    """
    return VacationRequest.objects.filter(
        employee=employee_profile,
        status__name__in=ACTIVE_REQUEST_STATUS_NAMES,
        start_date__lte=end_date,
        end_date__gte=start_date,
    )
