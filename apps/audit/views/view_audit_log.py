"""Vistas para consultar la actividad registrada en auditoria."""

from django.shortcuts import render

from apps.audit.selectors import get_audit_logs
from apps.core.utils.decorators import role_required
from apps.dashboard.services.layout_context import build_dashboard_base_context


@role_required("admin")
def audit_log_view(request):
    """Muestra un historial legible de acciones administrativas.

    Esta primera version se centra en eventos de gestion de usuarios y usa
    descripciones redactadas en castellano claro para que el panel resulte
    comodo de revisar sin conocimientos tecnicos.
    """

    audit_logs = get_audit_logs()
    return render(
        request,
        "audit/audit_log.html",
        build_dashboard_base_context(
            request.user,
            "admin",
            request=request,
            active_section="activity",
            extra_context={
                "audit_logs": audit_logs,
                "audit_logs_count": audit_logs.count(),
            },
        ),
    )
