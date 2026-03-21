"""Exportaciones publicas del dominio de empleados."""

from .department import Department
from .employee import Employee

__all__ = [
    "Department",
    "Employee",
]
