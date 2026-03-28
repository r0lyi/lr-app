"""Vistas administrativas para consultar y gestionar usuarios del sistema."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.users.models import Role, User
from apps.users.selectors import get_admin_user_list
from apps.users.services.admin_users import change_user_primary_role


@role_required("admin")
def admin_user_list_view(request):
    """Renderiza una lista basica de usuarios para el panel de admin.

    La logica del listado vive en ``apps.users.selectors`` para que el
    dashboard siga siendo una capa de presentacion y navegacion, no el sitio
    donde se concentran consultas de otros dominios.
    """

    managed_users = get_admin_user_list()
    available_roles = Role.objects.order_by("name")
    context = build_dashboard_base_context(
        request.user,
        "admin",
        request=request,
        active_section="users",
        extra_context={
            "managed_users": managed_users,
            "managed_users_count": len(managed_users),
            "available_roles": available_roles,
        },
    )
    return render(request, "users/admin_user_list.html", context)


@role_required("admin")
def admin_user_primary_role_update_view(request, user_id):
    """Procesa el cambio de rol principal desde el listado admin.

    La vista se mantiene muy fina:
    - recupera el usuario y el rol objetivo
    - delega las reglas al servicio del dominio ``users``
    - informa el resultado al admin con mensajes
    """

    if request.method != "POST":
        return redirect("dashboard:admin-users")

    target_user = get_object_or_404(
        User.objects.prefetch_related("roles"),
        pk=user_id,
    )
    role_id = request.POST.get("primary_role")
    new_role = Role.objects.filter(pk=role_id).first()

    if new_role is None:
        messages.error(request, "Selecciona un rol valido antes de guardar.")
        return redirect("dashboard:admin-users")

    try:
        change_user_primary_role(
            acting_user=request.user,
            target_user=target_user,
            new_role=new_role,
        )
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    else:
        messages.success(
            request,
            f"El rol principal de {target_user.email} se ha actualizado a {new_role.name}.",
        )

    return redirect("dashboard:admin-users")
