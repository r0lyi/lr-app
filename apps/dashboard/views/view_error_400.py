"""Vista de fallback para usuarios autenticados con configuracion inconsistente."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.users.selectors import get_primary_role


@login_required(login_url="/auth/login/")
def error_400_view(request):
    """Devuelve un 400 real cuando el usuario no tiene un rol valido."""
    if get_primary_role(request.user):
        return redirect("dashboard:home")
    return render(request, "dashboard/pages/error_400.html", status=400)
