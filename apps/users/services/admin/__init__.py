"""Servicios administrativos agrupados del dominio users."""

from .management import (
    change_user_active_state,
    change_user_department,
    change_user_primary_role,
)

__all__ = [
    "change_user_active_state",
    "change_user_department",
    "change_user_primary_role",
]
