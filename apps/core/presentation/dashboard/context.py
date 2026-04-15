"""Constructor central del contexto compartido del shell de dashboard."""

from .display import (
    get_dashboard_avatar_theme,
    get_dashboard_display_initials,
    get_dashboard_display_name,
)
from .navigation import get_dashboard_nav_items, get_role_label
from .notifications import get_dashboard_notifications_context


def build_dashboard_base_context(
    user,
    role_name,
    *,
    request=None,
    active_section="home",
    extra_context=None,
):
    """Devuelve el contexto comun usado por las pantallas del dashboard."""

    avatar_theme = get_dashboard_avatar_theme(user)

    context = {
        "display_name": get_dashboard_display_name(user),
        "display_initials": get_dashboard_display_initials(user),
        "display_avatar_background": avatar_theme["background"],
        "display_avatar_foreground": avatar_theme["foreground"],
        "role_label": get_role_label(role_name),
        "nav_items": get_dashboard_nav_items(
            role_name,
            active_section=active_section,
        ),
        **get_dashboard_notifications_context(user, request=request),
    }
    if extra_context:
        context.update(extra_context)
    return context
