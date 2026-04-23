"""Consultas de lectura usadas por el panel basico del empleado."""

from apps.employees.models import Employee


def get_employee_profile_for_user(user):
    """Devuelve la ficha Employee del usuario o None si aun no existe."""
    try:
        return user.employee_profile
    except Employee.DoesNotExist:
        return None
