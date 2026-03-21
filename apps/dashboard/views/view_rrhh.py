"""Vista minima del panel de recursos humanos."""

from django.shortcuts import render

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context


@role_required("rrhh", allow_admin=True)
def rrhh_home_view(request):
    """Muestra la vista basica de RRHH protegida por rol principal."""
    return render(
        request,
        "dashboard/rrhh_home.html",
        build_dashboard_base_context(request.user, "rrhh", active_section="home"),
    )
