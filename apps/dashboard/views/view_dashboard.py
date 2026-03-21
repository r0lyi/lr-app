"""Dispatcher principal del dashboard segun el rol del usuario autenticado."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from apps.employees.models import Employee
from apps.users.selectors import get_primary_role


@login_required(login_url="/auth/login/")
def home_view(request):
    """Redirige a la home basica correcta segun el rol principal."""
    primary_role = get_primary_role(request.user)

    if primary_role == "admin":
        return redirect("dashboard:admin-home")

    if primary_role == "rrhh":
        return redirect("dashboard:rrhh-home")

    if primary_role != "employee":
        return redirect("dashboard:error-400")

    # Un empleado necesita completar antes su ficha interna.
    try:
        request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect("employees:onboarding")

    return redirect("dashboard:employee-home")
