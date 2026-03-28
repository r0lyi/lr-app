"""Selectores del panel admin para resumen y listado de usuarios.

Estas funciones viven en el dominio ``users`` porque la informacion que
consumen y preparan pertenece a usuarios, roles y fichas de empleado. El
dashboard solo usa estos datos para pintarlos en pantalla.
"""

from apps.employees.models import Employee
from apps.users.models import User
from apps.vacations.models import VacationRequest

from .roles import PRIMARY_ROLE_PRIORITY

ROLE_LABELS = {
    "employee": "Empleado",
    "rrhh": "RRHH",
    "admin": "Administrador",
}


def _get_prefetched_primary_role_name(user):
    """Resuelve el rol principal usando los roles ya cargados en memoria.

    Esta variante evita consultas extra cuando el listado de usuarios ya viene
    con ``prefetch_related("roles")``. Asi mantenemos el panel admin ligero
    incluso si crece el numero de usuarios.
    """

    if getattr(user, "is_superuser", False):
        return "admin"

    role_names = {
        (role.name or "").strip().lower()
        for role in user.roles.all()
        if role.name
    }
    for role_name in PRIMARY_ROLE_PRIORITY:
        if role_name in role_names:
            return role_name
    return None


def _get_user_display_name(user):
    """Devuelve un nombre legible para usar en el listado del admin."""

    try:
        employee_profile = user.employee_profile
    except Employee.DoesNotExist:
        employee_profile = None

    if employee_profile is not None:
        full_name = (
            f"{employee_profile.first_name} {employee_profile.last_name}"
        ).strip()
        if full_name:
            return full_name

    email = (user.email or "").strip()
    if "@" in email:
        return email.split("@", 1)[0]
    return email or "Usuario"


def get_admin_dashboard_summary():
    """Construye el resumen general mostrado en la home de administracion.

    El objetivo de este resumen es que el admin vea en una sola pantalla una
    foto rapida del sistema: cuantos usuarios hay, cuantos estan activos,
    cuantas fichas ``Employee`` existen y cuantos registros de vacaciones se
    han generado hasta el momento.
    """

    return {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "total_employee_profiles": Employee.objects.count(),
        "total_vacation_requests": VacationRequest.objects.count(),
        "total_rrhh_users": User.objects.filter(roles__name="rrhh")
        .distinct()
        .count(),
        "total_admin_users": User.objects.filter(roles__name="admin")
        .distinct()
        .count(),
    }


def get_admin_user_list(*, limit=None):
    """Devuelve filas ya preparadas para el listado administrativo.

    La vista no necesita conocer detalles de roles o de la ficha ``Employee``.
    Solo recibe una lista simple y legible para mostrar nombre, correo, DNI,
    rol principal y estado del usuario.
    """

    users = (
        User.objects.select_related("employee_profile")
        .prefetch_related("roles")
        .order_by("email")
    )
    if limit is not None:
        users = users[:limit]

    user_rows = []
    for user in users:
        primary_role_name = _get_prefetched_primary_role_name(user)
        user_rows.append(
            {
                "user": user,
                "display_name": _get_user_display_name(user),
                "primary_role_name": primary_role_name,
                "primary_role_label": ROLE_LABELS.get(
                    primary_role_name,
                    "Sin rol",
                ),
                "has_employee_profile": hasattr(user, "employee_profile"),
            }
        )
    return user_rows
