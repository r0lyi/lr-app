"""Vistas del panel de gestion de solicitudes para RRHH y admin."""

from datetime import date

from django.urls import reverse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.presentation.pagination import paginate_dashboard_list
from apps.core.utils.decorators import role_required
from apps.users.selectors import get_primary_role
from apps.vacations.forms import RrhhVacationRequestFilterForm
from apps.vacations.selectors import get_filtered_rrhh_vacation_requests
from apps.vacations.services import build_rrhh_export_review


SPANISH_MONTH_ABBREVIATIONS = {
    1: _("Ene"),
    2: _("Feb"),
    3: _("Mar"),
    4: _("Abr"),
    5: _("May"),
    6: _("Jun"),
    7: _("Jul"),
    8: _("Ago"),
    9: _("Sep"),
    10: _("Oct"),
    11: _("Nov"),
    12: _("Dic"),
}


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
    export_review = build_rrhh_export_review(vacation_requests)
    reviewed_requests = export_review["vacation_requests"]
    requests_metrics = _build_rrhh_requests_metrics(reviewed_requests)
    requests_page = paginate_dashboard_list(request, reviewed_requests)

    export_querydict = filter_form.data.copy() if filter_form.is_bound else None
    if export_querydict is not None:
        export_querydict.pop("page", None)
    export_querystring = export_querydict.urlencode() if export_querydict else ""
    export_url = reverse("vacations:export-rrhh-requests-excel")
    if export_querystring:
        export_url = f"{export_url}?{export_querystring}"

    panel_title = _("Gestión de Solicitudes")
    panel_description = _("Control de ausencias y vacaciones del personal.")

    return render(
        request,
        "vacations/pages/requests_management.html",
        build_dashboard_base_context(
            request.user,
            role_name,
            request=request,
            active_section=active_section,
            extra_context={
                "export_url": export_url,
                "export_review_summary": export_review["summary"],
                "filter_form": filter_form,
                "vacation_requests": requests_page["items"],
                "filtered_requests_count": len(reviewed_requests),
                "page_obj": requests_page["page_obj"],
                "pagination_context": requests_page["pagination_context"],
                "requests_metrics": requests_metrics,
                "requests_page_title": panel_title,
                "requests_page_description": panel_description,
            },
        ),
    )


def _build_rrhh_requests_metrics(vacation_requests):
    """Construye los tres KPIs visibles en el panel de solicitudes."""

    today = date.today()
    current_month_count = _count_requests_in_month(
        vacation_requests,
        today.year,
        today.month,
    )
    previous_year, previous_month = _previous_month(today.year, today.month)
    previous_month_count = _count_requests_in_month(
        vacation_requests,
        previous_year,
        previous_month,
    )

    if previous_month_count:
        difference = current_month_count - previous_month_count
        percent = round(abs(difference) / previous_month_count * 100)
        if difference > 0:
            month_note = _("+%(percent)s%% vs mes anterior") % {"percent": percent}
        elif difference < 0:
            month_note = _("-%(percent)s%% vs mes anterior") % {"percent": percent}
        else:
            month_note = _("Sin variación vs mes anterior")
    else:
        month_note = _("Sin referencia del mes anterior")

    pending_requests_count = sum(
        1
        for vacation_request in vacation_requests
        if getattr(vacation_request.status, "name", "").lower() == "pending"
    )

    return [
        {
            "label": _("Total este mes"),
            "value": current_month_count,
            "unit": _("Solicitudes"),
            "note": month_note,
            "theme": "blue",
            "icon": "chart",
        },
        {
            "label": _("Pendientes de revisión"),
            "value": pending_requests_count,
            "unit": _("Solicitudes"),
            "note": _("Requieren atención")
            if pending_requests_count
            else _("Sin pendientes"),
            "theme": "amber",
            "icon": "clock",
        },
    ]


def _count_requests_in_month(vacation_requests, year, month):
    """Cuenta solicitudes cuyo inicio cae en un mes concreto."""

    return sum(
        1
        for vacation_request in vacation_requests
        if vacation_request.start_date.year == year
        and vacation_request.start_date.month == month
    )


def _previous_month(year, month):
    """Devuelve el mes anterior conservando el cambio de año."""

    if month == 1:
        return year - 1, 12
    return year, month - 1


def _format_spanish_date_range(start_date, end_date):
    """Formatea un rango corto de fechas con meses en español."""

    if start_date == end_date:
        return _format_spanish_day_month(start_date)

    if start_date.year == end_date.year and start_date.month == end_date.month:
        return (
            f"{start_date.day:02d} - {end_date.day:02d} "
            f"{SPANISH_MONTH_ABBREVIATIONS[start_date.month]}"
        )

    if start_date.year == end_date.year:
        return (
            f"{start_date.day:02d} {SPANISH_MONTH_ABBREVIATIONS[start_date.month]} - "
            f"{end_date.day:02d} {SPANISH_MONTH_ABBREVIATIONS[end_date.month]}"
        )

    return (
        f"{start_date.day:02d} {SPANISH_MONTH_ABBREVIATIONS[start_date.month]} "
        f"{start_date.year} - "
        f"{end_date.day:02d} {SPANISH_MONTH_ABBREVIATIONS[end_date.month]} "
        f"{end_date.year}"
    )


def _format_spanish_day_month(value):
    return f"{value.day:02d} {SPANISH_MONTH_ABBREVIATIONS[value.month]}"


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
