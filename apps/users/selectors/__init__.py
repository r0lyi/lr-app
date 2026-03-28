"""Exportaciones de selectores del dominio users."""

from .admin_users import get_admin_dashboard_summary, get_admin_user_list
from .roles import PRIMARY_ROLE_PRIORITY, get_primary_role, get_user_role_names, has_role

__all__ = [
    "get_admin_dashboard_summary",
    "get_admin_user_list",
    "PRIMARY_ROLE_PRIORITY",
    "get_primary_role",
    "get_user_role_names",
    "has_role",
]
