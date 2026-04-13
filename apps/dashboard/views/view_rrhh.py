"""Vistas del panel de gestion de solicitudes para RRHH y admin."""

from django.urls import reverse
from django.shortcuts import redirect, render

from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.users.selectors import get_primary_role
from apps.vacations.forms import RrhhVacationRequestFilterForm
from apps.vacations.selectors import get_filtered_rrhh_vacation_requests


def _render_requests_management_view(request, *, role_name, active_section):
    """Renderiza el panel compartido de solicitudes para RRHH o admin.

    La logica de lectura y filtrado sigue viviendo en ``vacations``. Aqui solo
    decidimos el contexto visual y la URL de exportacion que necesita el panel.
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

    panel_title = "Solicitudes"
    if role_name == "admin":
        panel_description = (
            "Gestiona y revisa las solicitudes registradas desde el panel de "
            "administracion sin salir de tu area de trabajo."
        )
    else:
        panel_description = (
            "Visualiza, filtra y revisa las solicitudes activas del equipo "
            "desde un solo panel."
        )

    return render(
        request,
        "dashboard/pages/requests_management.html",
        build_dashboard_base_context(
            request.user,
            role_name,
            request=request,
            active_section=active_section,
            extra_context={
                "export_url": export_url,
                "filter_form": filter_form,
                "vacation_requests": vacation_requests,
                "filtered_requests_count": vacation_requests.count(),
                "requests_page_title": panel_title,
                "requests_page_description": panel_description,
            },
        ),
    )


@role_required("rrhh", allow_admin=True)
def rrhh_home_view(request):
    """Muestra el panel de solicitudes para RRHH.

    Si entra un admin por esta ruta antigua, lo redirigimos a su entrada propia
    para mantener una experiencia consistente y un menu lateral correcto.
    """

    if get_primary_role(request.user) == "admin":
        return redirect("dashboard:admin-requests")

    return _render_requests_management_view(
        request,
        role_name="rrhh",
        active_section="home",
    )


@role_required("admin")
def admin_requests_view(request):
    """Muestra al admin la misma gestion de solicitudes que usa RRHH."""

    return _render_requests_management_view(
        request,
        role_name="admin",
        active_section="requests",
    )
