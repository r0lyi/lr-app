"""Vista minima del panel de administracion."""

from django.shortcuts import render

from apps.core.utils.decorators import role_required
from .helpers import build_dashboard_base_context


@role_required("admin")
def admin_home_view(request):
    """Muestra la vista basica de administracion protegida por rol."""
    return render(
        request,
        "dashboard/admin_home.html",
        build_dashboard_base_context(request.user, "admin", active_section="home"),
    )
