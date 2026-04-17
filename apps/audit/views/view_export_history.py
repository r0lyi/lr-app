"""Vistas para consultar y descargar el historial de exportaciones."""

from pathlib import Path

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.audit.forms import ExportHistoryFilterForm
from apps.audit.services import EXPORT_TYPE_RRHH_VACATION_REQUESTS
from apps.audit.selectors import get_export_histories
from apps.audit.models import ExportHistory
from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.presentation.pagination import paginate_dashboard_list
from apps.core.utils.decorators import role_required
from apps.users.selectors import get_primary_role


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

    export_histories = get_export_histories(
        export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
        start_date=filters.get("start_date"),
        end_date=filters.get("end_date"),
    )
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
                "page_obj": export_histories_page["page_obj"],
                "pagination_context": export_histories_page["pagination_context"],
                "filter_form": filter_form,
            },
        ),
    )


@role_required("rrhh", allow_admin=True)
def download_export_history_file_view(request, export_history_id):
    """Entrega un archivo ya exportado si sigue existiendo en disco."""

    export_history = get_object_or_404(
        ExportHistory.objects.select_related("user"),
        pk=export_history_id,
        export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
    )

    if not export_history.file_path:
        messages.error(request, "Esta exportacion no tiene archivo disponible.")
        return redirect("audit:export-history")

    export_path = Path(export_history.file_path)
    if not export_path.exists():
        messages.error(request, "No se encontro el archivo exportado en disco.")
        return redirect("audit:export-history")

    return FileResponse(
        export_path.open("rb"),
        as_attachment=True,
        filename=export_history.file_name or export_path.name,
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
