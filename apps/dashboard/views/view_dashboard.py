"""Dispatcher principal del dashboard segun el rol del usuario autenticado."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from apps.employees.selectors import get_employee_profile_for_user
from apps.users.selectors import get_primary_role


@login_required(login_url="/auth/login/")
def home_view(request):
    """Redirige a la home basica correcta segun el rol principal."""
    # El primer acceso de cualquier cuenta debe completar la ficha interna
    # de empleado, aunque el rol final sea admin o RRHH.
    if get_employee_profile_for_user(request.user) is None:
        return redirect("employees:onboarding")

    primary_role = get_primary_role(request.user)

    if primary_role == "admin":
        return redirect("dashboard:admin-home")

    if primary_role == "rrhh":
        return redirect("dashboard:rrhh-home")

    if primary_role != "employee":
        return redirect("dashboard:error-400")

    return redirect("dashboard:employee-home")
