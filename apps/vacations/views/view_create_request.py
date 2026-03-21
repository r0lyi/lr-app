"""Vista basica para que el empleado cree una solicitud de vacaciones."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.employees.selectors import get_employee_profile_for_user
from apps.employees.services.employee_dashboard import (
    calculate_annual_vacation_days_for_year,
)
from apps.vacations.forms import VacationRequestForm
from apps.vacations.services import create_employee_vacation_request


@role_required("employee")
def create_vacation_request_view(request):
    """Renderiza y procesa el formulario minimo de solicitud del empleado.

    Esta vista solo orquesta:
    - comprueba que exista el perfil Employee
    - valida el formulario
    - delega la creacion real al servicio del dominio vacations
    - recompone el contexto visual usando el layout del dashboard
    """
    employee_profile = get_employee_profile_for_user(request.user)
    if employee_profile is None:
        return redirect("employees:onboarding")

    if request.method == "POST":
        form = VacationRequestForm(request.POST)
        if form.is_valid():
            try:
                create_employee_vacation_request(
                    employee_profile,
                    start_date=form.cleaned_data["start_date"],
                    end_date=form.cleaned_data["end_date"],
                    employee_comment=form.cleaned_data["employee_comment"],
                )
            except ValidationError as exc:
                form.add_error(None, exc.message)
            else:
                messages.success(
                    request,
                    "Tu solicitud de vacaciones se ha registrado correctamente.",
                )
                return redirect("vacations:create-request")
    else:
        form = VacationRequestForm()

    current_year = timezone.localdate().year
    context = build_dashboard_base_context(
        request.user,
        "employee",
        active_section="request",
        extra_context={
            "form": form,
            "annual_vacation_reference_year": current_year,
            "annual_vacation_days_count": calculate_annual_vacation_days_for_year(
                employee_profile.hire_date,
                year=current_year,
            ),
        },
    )
    return render(request, "vacations/create_request.html", context)
