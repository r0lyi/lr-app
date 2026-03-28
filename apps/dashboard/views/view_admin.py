"""Vista principal del panel de administracion."""

from django.shortcuts import render

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.users.selectors import get_admin_dashboard_summary, get_admin_user_list


@role_required("admin")
def admin_home_view(request):
    """Muestra un resumen general del sistema para el rol admin.

    Esta home no pretende sustituir a las pantallas de gestion detallada. Su
    objetivo es ofrecer una fotografia general del sistema y un acceso rapido a
    la lista de usuarios, que es la primera herramienta util para un admin.
    """
    return render(
        request,
        "dashboard/admin_home.html",
        build_dashboard_base_context(
            request.user,
            "admin",
            request=request,
            active_section="home",
            extra_context={
                **get_admin_dashboard_summary(),
                "recent_users": get_admin_user_list(limit=5),
            },
        ),
    )
