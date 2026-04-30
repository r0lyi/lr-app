"""Vistas para consultar y descargar el historial de exportaciones."""

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from apps.audit.forms import ExportHistoryFilterForm
from apps.audit.services import EXPORT_TYPE_RRHH_VACATION_REQUESTS
from apps.audit.selectors import get_export_histories
from apps.audit.models import ExportHistory
from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.presentation.pagination import paginate_dashboard_list
from apps.core.utils.decorators import role_required
from apps.users.selectors import get_primary_role
from apps.vacations.services import (
    RRHH_EXPORT_COLUMNS,
    build_rrhh_vacation_requests_excel_from_snapshot,
)


@role_required("rrhh", allow_admin=True)
def export_history_view(request):
    """Muestra el historial basico de exportaciones del panel de RRHH."""
    current_role = get_primary_role(request.user) or "rrhh"

    if request.GET:
        filter_form = ExportHistoryFilterForm(request.GET)
        filters = (
            filter_form.cleaned_data if filter_form.is_valid() else {}
        )
    else:
        filter_form = ExportHistoryFilterForm()
        filters = {}

    all_export_histories = get_export_histories(
        export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
    )
    export_histories = get_export_histories(
        export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
        start_date=filters.get("start_date"),
        end_date=filters.get("end_date"),
    )
    total_exports_count = all_export_histories.count()
    latest_export = all_export_histories.first()
    export_histories_page = paginate_dashboard_list(request, export_histories)

    return render(
        request,
        "audit/pages/export_history.html",
        build_dashboard_base_context(
            request.user,
            current_role,
            request=request,
            active_section="requests" if current_role == "admin" else "history",
            extra_context={
                "export_histories": export_histories_page["items"],
                "filtered_exports_count": export_histories_page["total_count"],
                "total_exports_count": total_exports_count,
                "latest_export": latest_export,
                "page_obj": export_histories_page["page_obj"],
                "pagination_context": export_histories_page["pagination_context"],
                "filter_form": filter_form,
            },
        ),
    )


@role_required("rrhh", allow_admin=True)
def download_export_history_file_view(request, export_history_id):
    """Regenera y entrega un archivo ya exportado desde su snapshot."""

    export_history = get_object_or_404(
        ExportHistory.objects.select_related("user"),
        pk=export_history_id,
        export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
    )

    if export_history.rows_snapshot_json is None:
        messages.error(request, _("Esta exportacion no tiene snapshot disponible."))
        return redirect("audit:export-history")

    file_bytes = build_rrhh_vacation_requests_excel_from_snapshot(
        export_history.rows_snapshot_json
    )

    response = HttpResponse(
        file_bytes,
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{export_history.file_name or "export.xlsx"}"'
    )
    return response


@role_required("rrhh", allow_admin=True)
def preview_export_history_file_view(request, export_history_id):
    """Muestra una vista HTML del snapshot guardado para una exportacion."""

    export_history = get_object_or_404(
        ExportHistory.objects.select_related("user"),
        pk=export_history_id,
        export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
    )

    if export_history.rows_snapshot_json is None:
        messages.error(request, _("Esta exportacion no tiene snapshot disponible."))
        return redirect("audit:export-history")

    current_role = get_primary_role(request.user) or "rrhh"
    snapshot_rows = export_history.rows_snapshot_json or []

    return render(
        request,
        "audit/pages/export_preview.html",
        build_dashboard_base_context(
            request.user,
            current_role,
            request=request,
            active_section="requests" if current_role == "admin" else "history",
            extra_context={
                "export_history": export_history,
                "export_columns": RRHH_EXPORT_COLUMNS,
                "snapshot_rows": snapshot_rows,
                "snapshot_preview_count": len(snapshot_rows),
            },
        ),
    )
