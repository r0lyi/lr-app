"""Consultas de lectura usadas por el panel basico del empleado."""

from apps.employees.models import Employee
from apps.vacations.models import VacationRequest


def get_employee_profile_for_user(user):
    """Devuelve la ficha Employee del usuario o None si aun no existe."""
    try:
        return user.employee_profile
    except Employee.DoesNotExist:
        return None


def get_employee_requests(employee_profile):
    """Devuelve las solicitudes del empleado con el estado ya cargado."""
    return VacationRequest.objects.filter(
        employee=employee_profile,
    ).select_related("status").order_by("-request_date")
