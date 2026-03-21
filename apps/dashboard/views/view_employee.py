"""Vista minima del panel de empleado."""

from django.shortcuts import redirect, render

from apps.core.utils.decorators import role_required
from apps.employees.models import Employee
from .helpers import build_dashboard_base_context


@role_required("employee")
def employee_home_view(request):
    """Muestra el panel basico del empleado y exige ficha completada."""
    # Si aun no hay perfil, el empleado debe terminar el onboarding.
    try:
        employee_profile = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect("employees:onboarding")

    context = build_dashboard_base_context(
        request.user,
        "employee",
        active_section="home",
        extra_context={
            "employee_profile": employee_profile,
        },
    )
    return render(request, "dashboard/employee_home.html", context)
