"""Vista del panel basico de empleado dentro del dashboard principal."""

from django.shortcuts import redirect, render

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.employees.selectors.employee_dashboard import get_employee_profile_for_user
from apps.employees.services.employee_dashboard import build_employee_dashboard_summary
from apps.vacations.forms import EmployeeVacationRequestFilterForm


@role_required("employee")
def employee_home_view(request):
    """Renderiza la home del empleado usando la logica del dominio employees.

    La vista del dashboard se mantiene deliberadamente fina:
    - comprueba que el empleado ya tiene onboarding completado
    - pide al dominio employees el resumen de negocio
    - combina ese resumen con el contexto visual comun del dashboard

    Asi evitamos que el dominio dashboard acabe absorbiendo calculos y reglas
    que en realidad pertenecen a empleados o vacaciones.
    """
    employee_profile = get_employee_profile_for_user(request.user)
    if employee_profile is None:
        return redirect("employees:onboarding")

    filter_form = EmployeeVacationRequestFilterForm(request.GET or None)
    request_filters = filter_form.cleaned_data if filter_form.is_valid() else {}

    context = build_dashboard_base_context(
        request.user,
        "employee",
        request=request,
        active_section="home",
        extra_context={
            **build_employee_dashboard_summary(
                employee_profile,
                request_filters=request_filters,
            ),
            "filter_form": filter_form,
        },
    )
    return render(request, "dashboard/pages/employee_home.html", context)
