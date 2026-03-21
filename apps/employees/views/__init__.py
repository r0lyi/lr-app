"""Exportaciones publicas de vistas del dominio de empleados."""

from .view_employee_home import employee_home_view
from .onboarding import onboarding_view

__all__ = ["employee_home_view", "onboarding_view"]
