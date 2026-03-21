"""Vista minima del panel de administracion."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.users.selectors import get_primary_role
from .helpers import get_dashboard_display_name


@login_required(login_url="/auth/login/")
def admin_home_view(request):
    """Muestra la vista basica de admin si el rol principal es admin."""
    if get_primary_role(request.user) != "admin":
        return redirect("dashboard:home")

    return render(
        request,
        "dashboard/admin_home.html",
        {
            "display_name": get_dashboard_display_name(request.user),
            "role_label": "Administrador",
        },
    )
