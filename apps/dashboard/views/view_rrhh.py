"""Vista minima del panel de recursos humanos."""

from django.shortcuts import render

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.vacations.forms import RrhhVacationRequestFilterForm
from apps.vacations.selectors import get_filtered_rrhh_vacation_requests


@role_required("rrhh", allow_admin=True)
def rrhh_home_view(request):
    """Muestra el listado basico de solicitudes visible para RRHH.

    En esta primera iteracion RRHH no revisa ni filtra todavia: solo necesita
    una tabla sencilla para ver quien ha solicitado vacaciones y con que rango.
    """
    filter_form = RrhhVacationRequestFilterForm(request.GET or None)
    request_filters = filter_form.cleaned_data if filter_form.is_valid() else {}

    return render(
        request,
        "dashboard/rrhh_home.html",
        build_dashboard_base_context(
            request.user,
            "rrhh",
            active_section="home",
            extra_context={
                "filter_form": filter_form,
                "vacation_requests": get_filtered_rrhh_vacation_requests(
                    search=request_filters.get("search"),
                    start_date=request_filters.get("start_date"),
                    end_date=request_filters.get("end_date"),
                    status_name=request_filters.get("status"),
                ),
            },
        ),
    )
