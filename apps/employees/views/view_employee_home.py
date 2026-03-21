"""Vista del panel basico de empleado dentro del dashboard principal."""

from django.shortcuts import redirect, render

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.employees.selectors.employee_dashboard import get_employee_profile_for_user
from apps.employees.services.employee_dashboard import build_employee_dashboard_summary


@role_required("employee")
def employee_home_view(request):
    """Renderiza la home del empleado usando la logica del dominio employees."""
    employee_profile = get_employee_profile_for_user(request.user)
    if employee_profile is None:
        return redirect("employees:onboarding")

    context = build_dashboard_base_context(
        request.user,
        "employee",
        active_section="home",
        extra_context=build_employee_dashboard_summary(employee_profile),
    )
    return render(request, "dashboard/employee_home.html", context)
