"""Servicios administrativos agrupados del dominio users."""

from .management import (
    change_user_active_state,
    change_user_primary_role,
    delete_user_with_related_data,
    delete_users_with_related_data,
)

__all__ = [
    "change_user_active_state",
    "change_user_primary_role",
    "delete_user_with_related_data",
    "delete_users_with_related_data",
]
