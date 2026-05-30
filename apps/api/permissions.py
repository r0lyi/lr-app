"""Permisos reutilizables para la API interna."""

from rest_framework.permissions import BasePermission

from apps.users.selectors import has_role


class IsRrhhOrAdmin(BasePermission):
    """Permite acceso a usuarios con rol RRHH, admin o superusuario."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_superuser", False):
            return True
        return has_role(user, "rrhh") or has_role(user, "admin")


class IsSelfRrhhOrAdmin(BasePermission):
    """Permite ver datos propios o consultar como RRHH/admin."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_superuser", False):
            return True
        target_user_id = view.kwargs.get("user_id")
        return (
            user.pk == target_user_id
            or has_role(user, "rrhh")
            or has_role(user, "admin")
        )
