"""Vistas para consultar la actividad registrada en auditoria."""

from django.shortcuts import render

from apps.audit.forms import AuditLogFilterForm
from apps.audit.selectors import get_audit_log_summary, get_audit_logs
from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.utils.decorators import role_required


@role_required("admin")
def audit_log_view(request):
    """Muestra un historial legible de acciones administrativas.

    Esta primera version se centra en eventos de gestion de usuarios y usa
    descripciones redactadas en castellano claro para que el panel resulte
    comodo de revisar sin conocimientos tecnicos.
    """

    filter_form = AuditLogFilterForm(request.GET or None)
    filter_data = filter_form.cleaned_data if filter_form.is_valid() else None
    audit_logs = get_audit_logs(filters=filter_data)
    summary = get_audit_log_summary(filters=filter_data)
    return render(
        request,
        "audit/pages/audit_log.html",
        build_dashboard_base_context(
            request.user,
            "admin",
            request=request,
            active_section="activity",
            extra_context={
                "audit_logs": audit_logs,
                "audit_logs_count": audit_logs.count(),
                "audit_log_filter_form": filter_form,
                **summary,
            },
        ),
    )
