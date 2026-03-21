"""Vista minima del panel de empleado."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.employees.models import Employee
from apps.users.selectors import get_primary_role


@login_required(login_url="/auth/login/")
def employee_home_view(request):
    """Muestra el panel basico del empleado si su rol principal coincide."""
    if get_primary_role(request.user) != "employee":
        return redirect("dashboard:home")

    # Si aun no hay perfil, el empleado debe terminar el onboarding.
    try:
        employee_profile = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect("employees:onboarding")

    full_name = f"{employee_profile.first_name} {employee_profile.last_name}".strip()
    context = {
        "employee_profile": employee_profile,
        "user_display_name": full_name or request.user.email,
    }
    return render(request, "dashboard/employee_home.html", context)
