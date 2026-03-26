"""Helpers neutros para construir el layout comun del dashboard."""

from apps.employees.models import Employee

ROLE_LABELS = {
    "employee": "Empleado",
    "rrhh": "RRHH",
    "admin": "Administrador",
}

# Por ahora trabajamos con un unico panel funcional por rol. Si en el futuro
# se anaden mas vistas, este catalogo sera el sitio natural para extender el
# menu sin tocar cada template por separado.
ROLE_NAV_CONFIG = {
    "employee": [
        {
            "section": "home",
            "url_name": "dashboard:employee-home",
            "label": "Inicio",
            "icon": "home",
        },
        {
            "section": "request",
            "url_name": "vacations:create-request",
            "label": "Solicitar",
            "icon": "drop",
        },
        {
            "section": "profile",
            "url_name": "employees:profile",
            "label": "Perfil",
            "icon": "home",
        },
    ],
    "rrhh": [
        {
            "section": "home",
            "url_name": "dashboard:rrhh-home",
            "label": "Inicio",
            "icon": "home",
        },
        {
            "section": "history",
            "url_name": "audit:export-history",
            "label": "Historial",
            "icon": "home",
        },
        {
            "section": "profile",
            "url_name": "employees:profile",
            "label": "Perfil",
            "icon": "home",
        },
    ],
    "admin": [
        {
            "section": "home",
            "url_name": "dashboard:admin-home",
            "label": "Inicio",
            "icon": "home",
        },
        {
            "section": "profile",
            "url_name": "employees:profile",
            "label": "Perfil",
            "icon": "home",
        },
    ],
}


def get_dashboard_display_name(user):
    """Devuelve un nombre legible para el encabezado del dashboard."""
    try:
        profile = user.employee_profile
    except Employee.DoesNotExist:
        profile = None

    if profile is not None:
        full_name = f"{profile.first_name} {profile.last_name}".strip()
        if full_name:
            return full_name

    email = (user.email or "").strip()
    if "@" in email:
        return email.split("@", 1)[0]
    return email or "Usuario"


def get_role_label(role_name):
    """Traduce el nombre interno del rol a una etiqueta legible."""
    return ROLE_LABELS.get(role_name, "Usuario")


def get_dashboard_nav_items(role_name, *, active_section="home"):
    """Construye el menu lateral segun el rol principal activo."""
    items = []
    for item in ROLE_NAV_CONFIG.get(role_name, []):
        items.append(
            {
                **item,
                "active": item["section"] == active_section,
            }
        )
    return items


def build_dashboard_base_context(
    user,
    role_name,
    *,
    active_section="home",
    extra_context=None,
):
    """Devuelve el contexto comun usado por las pantallas del dashboard."""
    context = {
        "display_name": get_dashboard_display_name(user),
        "role_label": get_role_label(role_name),
        "nav_items": get_dashboard_nav_items(
            role_name,
            active_section=active_section,
        ),
    }
    if extra_context:
        context.update(extra_context)
    return context
