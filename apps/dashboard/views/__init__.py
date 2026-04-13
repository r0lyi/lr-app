"""Exportaciones publicas de vistas del dashboard."""

from apps.employees.views import employee_home_view
from apps.users.views import (
    admin_user_active_state_update_view,
    admin_user_department_update_view,
    admin_user_edit_view,
    admin_user_list_view,
    admin_user_primary_role_update_view,
)
from apps.vacations.views import admin_requests_view, rrhh_home_view

from .view_admin import admin_home_view
from .view_dashboard import home_view
from .view_error_400 import error_400_view

__all__ = [
    "admin_home_view",
    "admin_requests_view",
    "admin_user_active_state_update_view",
    "admin_user_department_update_view",
    "admin_user_edit_view",
    "admin_user_list_view",
    "admin_user_primary_role_update_view",
    "employee_home_view",
    "error_400_view",
    "home_view",
    "rrhh_home_view",
]
