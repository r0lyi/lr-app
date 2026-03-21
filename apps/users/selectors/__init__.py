"""Exportaciones de helpers para consultar roles de usuarios."""

from .roles import PRIMARY_ROLE_PRIORITY, get_primary_role, get_user_role_names, has_role

__all__ = [
    "PRIMARY_ROLE_PRIORITY",
    "get_primary_role",
    "get_user_role_names",
    "has_role",
]
