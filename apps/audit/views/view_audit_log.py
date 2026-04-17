"""Vistas para consultar la actividad registrada en auditoria."""

from django.shortcuts import render

from apps.audit.forms import AuditLogFilterForm
from apps.audit.selectors import get_audit_log_summary, get_audit_logs
from apps.audit.services import AUDIT_RESOURCE_TYPE_USER
from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.presentation.pagination import paginate_dashboard_list
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
    audit_logs_page = paginate_dashboard_list(request, audit_logs)
    summary = get_audit_log_summary(filters=filter_data)
    audit_summary_cards = [
        {
            "label": "Total Actividades",
            "value": summary["total_visible_activity"],
            "icon": "chart",
            "tone": "blue",
            "meta": "En tiempo real",
        },
        {
            "label": "Cambios de Rol",
            "value": summary["visible_role_changes"],
            "icon": "id-card",
            "tone": "orange",
        },
        {
            "label": "Cambios de Acceso",
            "value": summary["visible_access_changes"],
            "icon": "shield",
            "tone": "slate",
        },
    ]
    return render(
        request,
        "audit/pages/audit_log.html",
        build_dashboard_base_context(
            request.user,
            "admin",
            request=request,
            active_section="activity",
            extra_context={
                "audit_logs": audit_logs_page["items"],
                "audit_logs_count": audit_logs_page["total_count"],
                "page_obj": audit_logs_page["page_obj"],
                "pagination_context": audit_logs_page["pagination_context"],
                "audit_log_filter_form": filter_form,
                "audit_summary_cards": audit_summary_cards,
                "audit_resource_type_user": AUDIT_RESOURCE_TYPE_USER,
                **summary,
            },
        ),
    )
