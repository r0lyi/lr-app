"""Vista minima del panel de recursos humanos."""

from django.urls import reverse
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
    default_status_name = "pending"

    if request.GET:
        filter_data = request.GET.copy()
        # Si RRHH abre la pantalla sin tocar el selector de estado, dejamos
        # aplicado `pending` por defecto. Si el usuario envia `status=""`,
        # respetamos esa decision para mostrar todos.
        if "status" not in filter_data:
            filter_data["status"] = default_status_name
        filter_form = RrhhVacationRequestFilterForm(filter_data)
        request_filters = (
            filter_form.cleaned_data
            if filter_form.is_valid()
            else {"status": default_status_name}
        )
    else:
        filter_form = RrhhVacationRequestFilterForm(
            initial={"status": default_status_name}
        )
        request_filters = {"status": default_status_name}

    vacation_requests = get_filtered_rrhh_vacation_requests(
        search=request_filters.get("search"),
        start_date=request_filters.get("start_date"),
        end_date=request_filters.get("end_date"),
        status_name=request_filters.get("status"),
    )
    export_querystring = filter_form.data.urlencode() if filter_form.is_bound else ""
    export_url = reverse("vacations:export-rrhh-requests-excel")
    if export_querystring:
        export_url = f"{export_url}?{export_querystring}"

    return render(
        request,
        "dashboard/rrhh_home.html",
        build_dashboard_base_context(
            request.user,
            "rrhh",
            active_section="home",
            extra_context={
                "export_url": export_url,
                "filter_form": filter_form,
                "vacation_requests": vacation_requests,
                "filtered_requests_count": vacation_requests.count(),
            },
        ),
    )
