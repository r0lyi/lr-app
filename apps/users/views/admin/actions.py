"""Acciones POST del panel admin de usuarios."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from apps.core.utils.decorators import role_required
from apps.employees.models import Department
from apps.users.models import Role, User
from apps.users.services.admin.management import (
    change_user_active_state,
    change_user_department,
    change_user_primary_role,
)

from .common import redirect_to_admin_users_target


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
    desired_state = request.POST.get("is_active") == "1"

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


@role_required("admin")
def admin_user_department_update_view(request, user_id):
    """Actualiza el departamento asociado a la ficha Employee del usuario."""

    if request.method != "POST":
        return redirect_to_admin_users_target(request)

    target_user = get_object_or_404(
        User.objects.select_related("employee_profile__department").prefetch_related(
            "roles"
        ),
        pk=user_id,
    )
    department_id = (request.POST.get("department") or "").strip()
    new_department = Department.objects.filter(pk=department_id).first()

    if department_id and new_department is None:
        messages.error(
            request,
            "Selecciona un departamento valido antes de guardar.",
        )
        return redirect_to_admin_users_target(request)

    try:
        change_user_department(
            acting_user=request.user,
            target_user=target_user,
            new_department=new_department,
        )
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    else:
        department_label = new_department.name if new_department else "Sin departamento"
        messages.success(
            request,
            f"El departamento de {target_user.email} se ha actualizado a {department_label}.",
        )

    return redirect_to_admin_users_target(request)
