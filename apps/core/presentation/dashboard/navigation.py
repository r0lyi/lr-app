"""Configuracion del menu lateral y etiquetas del dashboard."""

from django.utils.translation import gettext_lazy as _


ROLE_LABELS = {
    "employee": _("Empleado"),
    "rrhh": _("RRHH"),
    "admin": _("Administrador"),
}

ROLE_NAV_CONFIG = {
    "employee": [
        {
            "section": "home",
            "url_name": "dashboard:employee-home",
            "label": _("Inicio"),
            "icon": "drop",
        },
        {
            "section": "request",
            "url_name": "vacations:create-request",
            "label": _("Solicitar"),
            "icon": "drop",
        },
        {
            "section": "profile",
            "url_name": "employees:profile",
            "label": _("Perfil"),
            "icon": "drop",
        },
    ],
    "rrhh": [
        {
            "section": "home",
            "url_name": "dashboard:rrhh-home",
            "label": _("Inicio"),
            "icon": "drop",
        },
        {
            "section": "request",
            "url_name": "vacations:create-request",
            "label": _("Solicitar"),
            "icon": "drop",
        },
        {
            "section": "history",
            "url_name": "audit:export-history",
            "label": _("Historial"),
            "icon": "drop",
        },
        {
            "section": "profile",
            "url_name": "employees:profile",
            "label": _("Perfil"),
            "icon": "drop",
        },
    ],
    "admin": [
        {
            "section": "home",
            "url_name": "dashboard:admin-home",
            "label": _("Inicio"),
            "icon": "drop",
        },
        {
            "section": "request",
            "url_name": "vacations:create-request",
            "label": _("Solicitar"),
            "icon": "drop",
        },
        {
            "section": "requests",
            "url_name": "dashboard:admin-requests",
            "label": _("Solicitudes"),
            "icon": "drop",
        },
        {
            "section": "users",
            "url_name": "dashboard:admin-users",
            "label": _("Usuarios"),
            "icon": "drop",
        },
        {
            "section": "activity",
            "url_name": "audit:activity-log",
            "label": _("Actividad"),
            "icon": "drop",
        },
        {
            "section": "profile",
            "url_name": "employees:profile",
            "label": _("Perfil"),
            "icon": "drop",
        },
    ],
}


def get_role_label(role_name):
    """Traduce el nombre interno del rol a una etiqueta legible."""

    return ROLE_LABELS.get(role_name, _("Usuario"))


def get_dashboard_nav_items(role_name, *, active_section="home"):
    """Construye el menu lateral segun el rol principal activo."""

    return [
        {
            **item,
            "active": item["section"] == active_section,
        }
        for item in ROLE_NAV_CONFIG.get(role_name, [])
    ]
