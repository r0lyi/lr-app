"""Vista administrativa para consultar el listado de usuarios del sistema."""

from django.shortcuts import render

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.users.selectors import get_admin_user_list


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
            "managed_users": managed_users,
            "managed_users_count": len(managed_users),
        },
    )
    return render(request, "users/admin_user_list.html", context)
