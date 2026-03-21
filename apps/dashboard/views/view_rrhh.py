"""Vista minima del panel de recursos humanos."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.users.selectors import get_primary_role


@login_required(login_url="/auth/login/")
def rrhh_home_view(request):
    """Muestra la vista basica de RRHH si el rol principal es rrhh."""
    if get_primary_role(request.user) != "rrhh":
        return redirect("dashboard:home")

    return render(request, "dashboard/rrhh_home.html")
