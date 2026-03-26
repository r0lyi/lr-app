"""Helpers neutros para construir el layout comun del dashboard."""

from apps.employees.models import Employee
from apps.notifications.selectors import (
    get_unread_notifications_count,
    get_user_inbox_notifications_page,
)

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


def build_notifications_page_url(request, page_number):
    """Construye una URL que conserva los filtros actuales y cambia de pagina."""

    if request is None:
        return ""

    query_params = request.GET.copy()
    query_params["notifications_page"] = page_number
    encoded_query = query_params.urlencode()
    return f"{request.path}?{encoded_query}" if encoded_query else request.path


def build_dashboard_base_context(
    user,
    role_name,
    *,
    request=None,
    active_section="home",
    extra_context=None,
):
    """Devuelve el contexto comun usado por las pantallas del dashboard."""
    notifications_page_number = 1
    if request is not None:
        notifications_page_number = request.GET.get("notifications_page", 1)

    notifications_page = get_user_inbox_notifications_page(
        user,
        page_number=notifications_page_number,
        page_size=10,
    )

    context = {
        "display_name": get_dashboard_display_name(user),
        "role_label": get_role_label(role_name),
        "nav_items": get_dashboard_nav_items(
            role_name,
            active_section=active_section,
        ),
        "notifications_page_obj": notifications_page,
        "recent_notifications": list(notifications_page.object_list),
        "notifications_next_page_url": (
            build_notifications_page_url(
                request,
                notifications_page.next_page_number(),
            )
            if notifications_page.has_next()
            else ""
        ),
        "notifications_previous_page_url": (
            build_notifications_page_url(
                request,
                notifications_page.previous_page_number(),
            )
            if notifications_page.has_previous()
            else ""
        ),
        "notifications_return_path": (
            request.get_full_path() if request is not None else ""
        ),
        "unread_notifications_count": get_unread_notifications_count(user),
    }
    if extra_context:
        context.update(extra_context)
    return context
