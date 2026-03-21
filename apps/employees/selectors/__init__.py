"""Selectores reservados para consultas del dominio de empleados."""

from .employee_dashboard import get_employee_profile_for_user, get_employee_requests

__all__ = [
    "get_employee_profile_for_user",
    "get_employee_requests",
]
