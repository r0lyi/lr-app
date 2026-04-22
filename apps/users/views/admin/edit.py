"""Pantalla individual de edicion de usuarios."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext as _

from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.utils.decorators import role_required
from apps.users.models import Role, User
from apps.users.services.admin import change_user_active_state, change_user_primary_role
from apps.users.selectors import get_admin_user_detail

from .common import parse_boolean_post_value, redirect_to_admin_users_target


@role_required("admin")
def admin_user_edit_view(request, user_id):
    """Renderiza una pantalla individual para gestionar un usuario."""

    if request.method == "POST":
        return _handle_admin_user_edit_post(request, user_id)

    try:
        managed_user = get_admin_user_detail(user_id=user_id)
    except User.DoesNotExist as exc:
        raise Http404(_("Usuario no encontrado.")) from exc

    context = build_dashboard_base_context(
        request.user,
        "admin",
        request=request,
        active_section="users",
        extra_context={
            "managed_user": managed_user,
            "available_roles": Role.objects.order_by("name"),
        },
    )
    return render(request, "users/pages/admin/user_edit.html", context)


def _handle_admin_user_edit_post(request, user_id):
    """Actualiza rol y estado de acceso desde el modal de edicion."""

    try:
        target_user = User.objects.prefetch_related("roles").get(pk=user_id)
    except User.DoesNotExist as exc:
        raise Http404(_("Usuario no encontrado.")) from exc

    new_role = Role.objects.filter(pk=request.POST.get("primary_role")).first()
    desired_state = parse_boolean_post_value(request.POST.get("is_active"))

    if new_role is None:
        messages.error(request, _("Selecciona un rol valido antes de guardar."))
        return redirect_to_admin_users_target(request)

    if desired_state is None:
        messages.error(request, _("Selecciona un estado de acceso valido."))
        return redirect_to_admin_users_target(request)

    try:
        with transaction.atomic():
            change_user_primary_role(
                acting_user=request.user,
                target_user=target_user,
                new_role=new_role,
            )
            change_user_active_state(
                acting_user=request.user,
                target_user=target_user,
                is_active=desired_state,
            )
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    else:
        messages.success(
            request,
            _("Los datos de acceso de %(email)s se han actualizado.")
            % {"email": target_user.email},
        )

    return redirect_to_admin_users_target(request)
