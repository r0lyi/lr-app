"""Exportaciones publicas de vistas del dashboard."""

from apps.employees.views import employee_home_view
from apps.users.views import admin_user_list_view

from .view_admin import admin_home_view
from .view_dashboard import home_view
from .view_error_400 import error_400_view
from .view_rrhh import rrhh_home_view

__all__ = [
    "admin_home_view",
    "admin_user_list_view",
    "employee_home_view",
    "error_400_view",
    "home_view",
    "rrhh_home_view",
]
