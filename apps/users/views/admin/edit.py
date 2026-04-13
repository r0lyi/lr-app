"""Pantalla individual de edicion de usuarios."""

from django.http import Http404
from django.shortcuts import render

from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.utils.decorators import role_required
from apps.employees.models import Department
from apps.users.models import Role, User
from apps.users.selectors import get_admin_user_detail


@role_required("admin")
def admin_user_edit_view(request, user_id):
    """Renderiza una pantalla individual para gestionar un usuario."""

    try:
        managed_user = get_admin_user_detail(user_id=user_id)
    except User.DoesNotExist as exc:
        raise Http404("Usuario no encontrado.") from exc

    context = build_dashboard_base_context(
        request.user,
        "admin",
        request=request,
        active_section="users",
        extra_context={
            "managed_user": managed_user,
            "available_roles": Role.objects.order_by("name"),
            "available_departments": Department.objects.order_by("name"),
        },
    )
    return render(request, "users/pages/admin/user_edit.html", context)
