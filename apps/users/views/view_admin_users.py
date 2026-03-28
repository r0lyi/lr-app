"""Vistas administrativas para consultar y gestionar usuarios del sistema."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.employees.models import Department
from apps.users.models import Role, User
from apps.users.selectors import (
    get_admin_dashboard_summary,
    get_admin_user_detail,
    get_admin_user_list,
)
from apps.users.services.admin_users import (
    change_user_active_state,
    change_user_department,
    change_user_primary_role,
)


def _redirect_to_admin_users_target(request):
    """Devuelve una redirección segura al destino deseado tras guardar.

    El panel ahora puede lanzar acciones tanto desde el listado como desde la
    pantalla individual de edición. Con este helper evitamos duplicar lógica
    y mantenemos una redirección segura dentro del mismo sitio.
    """

    next_url = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("dashboard:admin-users")


@role_required("admin")
def admin_user_list_view(request):
    """Renderiza una lista basica de usuarios para el panel de admin.

    La logica del listado vive en ``apps.users.selectors`` para que el
    dashboard siga siendo una capa de presentacion y navegacion, no el sitio
    donde se concentran consultas de otros dominios.
    """

    managed_users = get_admin_user_list()
    context = build_dashboard_base_context(
        request.user,
        "admin",
        request=request,
        active_section="users",
        extra_context={
            **get_admin_dashboard_summary(),
            "managed_users": managed_users,
            "managed_users_count": len(managed_users),
        },
    )
    return render(request, "users/admin_user_list.html", context)


@role_required("admin")
def admin_user_edit_view(request, user_id):
    """Renderiza una pantalla individual para gestionar un usuario.

    El listado de usuarios queda mas limpio y esta vista concentra las
    acciones de administracion habituales: rol, departamento y acceso.
    """

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
    return render(request, "users/admin_user_edit.html", context)


@role_required("admin")
def admin_user_primary_role_update_view(request, user_id):
    """Procesa el cambio de rol principal desde el listado admin.

    La vista se mantiene muy fina:
    - recupera el usuario y el rol objetivo
    - delega las reglas al servicio del dominio ``users``
    - informa el resultado al admin con mensajes
    """

    if request.method != "POST":
        return _redirect_to_admin_users_target(request)

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

    return _redirect_to_admin_users_target(request)


@role_required("admin")
def admin_user_active_state_update_view(request, user_id):
    """Activa o desactiva una cuenta desde la tabla de usuarios."""

    if request.method != "POST":
        return _redirect_to_admin_users_target(request)

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

    return _redirect_to_admin_users_target(request)


@role_required("admin")
def admin_user_department_update_view(request, user_id):
    """Actualiza el departamento asociado a la ficha Employee del usuario."""

    if request.method != "POST":
        return _redirect_to_admin_users_target(request)

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
        return _redirect_to_admin_users_target(request)

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

    return _redirect_to_admin_users_target(request)
