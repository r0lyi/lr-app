"""Vista basica para que el empleado cree una solicitud de vacaciones."""

from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.utils.decorators import role_required
from apps.employees.selectors import get_employee_profile_for_user
from apps.employees.services.employee_dashboard import (
    calculate_annual_vacation_days_for_year,
)
from apps.users.selectors import get_primary_role
from apps.vacations.forms import VacationRequestForm
from apps.vacations.services.requests.policies import MIN_ADVANCE_NOTICE_DAYS
from apps.vacations.services import (
    create_employee_vacation_request,
    get_request_annual_balance,
)


@role_required("employee", allow_admin=True, allow_rrhh=True)
def create_vacation_request_view(request):
    """Renderiza y procesa el formulario minimo de solicitud del usuario.

    Esta vista solo orquesta:
    - comprueba que exista el perfil Employee
    - valida el formulario
    - delega la creacion real al servicio del dominio vacations
    - recompone el contexto visual usando el layout del dashboard

    Aunque el flujo principal pertenece al rol ``employee``, tambien dejamos
    entrar a ``admin`` y ``rrhh`` para poder registrar solicitudes reales
    desde la propia aplicacion sin depender de cambios manuales en base de
    datos.
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
                for error_message in exc.messages:
                    form.add_error(None, error_message)
            else:
                messages.success(
                    request,
                    "Tu solicitud de vacaciones se ha registrado correctamente.",
                )
                return redirect("vacations:create-request")
    else:
        form = VacationRequestForm()

    today = timezone.localdate()
    current_year = today.year
    min_request_start_date = today + timedelta(days=MIN_ADVANCE_NOTICE_DAYS)
    current_role = get_primary_role(request.user) or "employee"
    annual_vacation_days_count = calculate_annual_vacation_days_for_year(
        employee_profile.hire_date,
        year=current_year,
    )
    annual_vacation_remaining_days_count = get_request_annual_balance(
        employee_profile,
        year=current_year,
    )
    annual_vacation_balance_percentage = 0.0
    if annual_vacation_days_count:
        annual_vacation_balance_percentage = round(
            max(
                0.0,
                min(
                    100.0,
                    (
                        float(annual_vacation_remaining_days_count)
                        / float(annual_vacation_days_count)
                    )
                    * 100.0,
                ),
            ),
            2,
        )

    context = build_dashboard_base_context(
        request.user,
        current_role,
        request=request,
        active_section="request",
        extra_context={
            "form": form,
            "annual_vacation_reference_year": current_year,
            "annual_vacation_days_count": annual_vacation_days_count,
            "annual_vacation_remaining_days_count": annual_vacation_remaining_days_count,
            "annual_vacation_balance_percentage": annual_vacation_balance_percentage,
            "min_request_start_date": min_request_start_date,
            "min_advance_notice_days": MIN_ADVANCE_NOTICE_DAYS,
        },
    )
    return render(request, "vacations/pages/create_request.html", context)
