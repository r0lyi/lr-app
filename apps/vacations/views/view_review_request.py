"""Vista basica para que RRHH revise una solicitud concreta."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.vacations.forms import VacationRequestReviewForm
from apps.vacations.models import VacationRequest
from apps.vacations.services import review_vacation_request


@role_required("rrhh", allow_admin=True)
def review_vacation_request_view(request, request_id):
    """Permite a RRHH cambiar estado y fechas de una solicitud concreta."""

    vacation_request = get_object_or_404(
        VacationRequest.objects.select_related("employee", "status"),
        pk=request_id,
    )

    if request.method == "POST":
        form = VacationRequestReviewForm(request.POST)
        if form.is_valid():
            try:
                review_vacation_request(
                    vacation_request,
                    acting_user=request.user,
                    status=form.cleaned_data["status"],
                    start_date=form.cleaned_data["start_date"],
                    end_date=form.cleaned_data["end_date"],
                    hr_comment=form.cleaned_data["hr_comment"],
                )
            except ValidationError as exc:
                form.add_error(None, exc.message)
            else:
                messages.success(
                    request,
                    "La solicitud se ha actualizado correctamente desde RRHH.",
                )
                return redirect("dashboard:rrhh-home")
    else:
        form = VacationRequestReviewForm(
            initial={
                "status": vacation_request.status,
                "start_date": vacation_request.start_date,
                "end_date": vacation_request.end_date,
                "hr_comment": vacation_request.hr_comment,
            }
        )

    context = build_dashboard_base_context(
        request.user,
        "rrhh",
        active_section="home",
        extra_context={
            "vacation_request": vacation_request,
            "form": form,
        },
    )
    return render(request, "vacations/review_request.html", context)
