"""Vista para eliminar solicitudes pendientes del empleado."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _

from apps.core.utils.decorators import role_required
from apps.employees.selectors import get_employee_profile_for_user
from apps.vacations.models import VacationRequest
from apps.vacations.services import delete_pending_vacation_request


@role_required("employee")
def delete_vacation_request_view(request, request_id):
    """Elimina una solicitud propia si aun esta pendiente."""

    if request.method != "POST":
        return redirect("dashboard:employee-home")

    employee_profile = get_employee_profile_for_user(request.user)
    if employee_profile is None:
        return redirect("employees:onboarding")

    vacation_request = get_object_or_404(
        VacationRequest.objects.select_related("employee", "status"),
        pk=request_id,
        employee=employee_profile,
    )

    try:
        delete_pending_vacation_request(vacation_request)
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    else:
        messages.success(
            request, _("La solicitud pendiente se ha eliminado correctamente.")
        )

    return redirect("dashboard:employee-home")
