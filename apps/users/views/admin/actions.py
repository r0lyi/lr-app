"""Acciones POST del panel admin de usuarios."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from apps.core.utils.decorators import role_required
from apps.users.models import Role, User
from apps.users.services.admin.management import (
    change_user_active_state,
    change_user_primary_role,
)

from .common import parse_boolean_post_value, redirect_to_admin_users_target


@role_required("admin")
def admin_user_primary_role_update_view(request, user_id):
    """Procesa el cambio de rol principal desde el listado admin."""

    if request.method != "POST":
        return redirect_to_admin_users_target(request)

    target_user = get_object_or_404(
        User.objects.prefetch_related("roles"),
        pk=user_id,
    )
    role_id = request.POST.get("primary_role")
    new_role = Role.objects.filter(pk=role_id).first()

    if new_role is None:
        messages.error(request, "Selecciona un rol valido antes de guardar.")
        return redirect_to_admin_users_target(request)

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

    return redirect_to_admin_users_target(request)


@role_required("admin")
def admin_user_active_state_update_view(request, user_id):
    """Activa o desactiva una cuenta desde la tabla de usuarios."""

    if request.method != "POST":
        return redirect_to_admin_users_target(request)

    target_user = get_object_or_404(
        User.objects.prefetch_related("roles"),
        pk=user_id,
    )
    desired_state = parse_boolean_post_value(request.POST.get("is_active"))
    if desired_state is None:
        messages.error(request, "Selecciona un estado de acceso valido.")
        return redirect_to_admin_users_target(request)

    try:
        change_user_active_state(
            acting_user=request.user,
            target_user=target_user,
            is_active=desired_state,
        )
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    else:
        if desired_state:
            messages.success(
                request,
                f"La cuenta de {target_user.email} ha quedado activada.",
            )
        else:
            messages.success(
                request,
                f"La cuenta de {target_user.email} ha quedado desactivada.",
            )

    return redirect_to_admin_users_target(request)
