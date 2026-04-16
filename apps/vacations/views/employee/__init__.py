"""Vistas del area de empleado dentro del dominio vacations."""

from .create_request import create_vacation_request_view
from .delete_request import delete_vacation_request_view

__all__ = [
    "create_vacation_request_view",
    "delete_vacation_request_view",
]
