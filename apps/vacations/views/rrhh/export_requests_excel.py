"""Vista para exportar a Excel las solicitudes filtradas de RRHH."""

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _

from apps.audit.services import (
    EXPORT_TYPE_RRHH_VACATION_REQUESTS,
    create_export_history,
    mark_export_failed,
    mark_export_success,
)
from apps.core.utils.decorators import role_required
from apps.users.selectors import get_primary_role
from apps.vacations.forms import RrhhVacationRequestFilterForm
from apps.vacations.selectors import get_filtered_rrhh_vacation_requests
from apps.vacations.services import build_rrhh_export_review
from apps.vacations.services.export.excel import (
    RRHH_EXPORT_COLUMNS_VERSION,
    build_rrhh_vacation_requests_excel,
)


@role_required("rrhh", allow_admin=True)
def export_rrhh_requests_excel_view(request):
    """Genera y descarga el Excel del listado actual de RRHH.

    La vista reutiliza exactamente los mismos filtros que el panel de RRHH
    para evitar que el usuario descargue un resultado distinto al que ve.
    """

    default_status_name = "pending"
    current_role = get_primary_role(request.user) or "rrhh"
    return_url_name = (
        "dashboard:admin-requests" if current_role == "admin" else "dashboard:rrhh-home"
    )
    filter_data = request.GET.copy()
    if "status" not in filter_data:
        filter_data["status"] = default_status_name

    filter_form = RrhhVacationRequestFilterForm(filter_data)
    if not filter_form.is_valid():
        messages.error(
            request,
            _("No se pudo exportar porque los filtros enviados no son validos."),
        )
        return redirect(return_url_name)

    request_filters = filter_form.cleaned_data
    vacation_requests = get_filtered_rrhh_vacation_requests(
        search=request_filters.get("search"),
        start_date=request_filters.get("start_date"),
        end_date=request_filters.get("end_date"),
        status_name=request_filters.get("status"),
    )
    export_review = build_rrhh_export_review(vacation_requests)
    reviewed_requests = export_review["vacation_requests"]

    export_history = create_export_history(
        user=request.user,
        export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
        filters=request_filters,
    )

    try:
        file_name, file_bytes, snapshot_rows = build_rrhh_vacation_requests_excel(
            reviewed_requests
        )
        mark_export_success(
            export_history=export_history,
            file_name=file_name,
            rows_snapshot=snapshot_rows,
            columns_version=RRHH_EXPORT_COLUMNS_VERSION,
            total_records=len(reviewed_requests),
        )
    except Exception:
        mark_export_failed(export_history=export_history)
        messages.error(
            request,
            _("No se pudo generar el archivo Excel de las solicitudes."),
        )
        return redirect(return_url_name)

    response = HttpResponse(
        file_bytes,
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'
    return response
