"""Selectores de lectura para el historial de auditoria."""

from django.db.models import Q

from apps.audit.models import AuditLog


def get_audit_logs(*, action=None, resource_type=None, limit=None, filters=None):
    """Devuelve el historial de auditoria listo para pintar en pantalla."""

    audit_logs = _build_filtered_audit_logs(
        action=action,
        resource_type=resource_type,
        filters=filters,
    )

    if limit is not None:
        audit_logs = audit_logs[:limit]

    return audit_logs


def get_audit_log_summary(*, filters=None):
    """Calcula contadores útiles para resumir la actividad visible."""

    audit_logs = _build_filtered_audit_logs(filters=filters)
    return {
        "total_visible_activity": audit_logs.count(),
        "visible_role_changes": audit_logs.filter(
            action="user_primary_role_changed"
        ).count(),
        "visible_access_changes": audit_logs.filter(
            action="user_access_state_changed"
        ).count(),
        "visible_department_changes": audit_logs.filter(
            action="user_department_changed"
        ).count(),
    }


def _build_filtered_audit_logs(*, action=None, resource_type=None, filters=None):
    """Aplica filtros reutilizables sobre el historial de auditoría."""

    audit_logs = AuditLog.objects.select_related("user").order_by("-created_at")

    if action:
        audit_logs = audit_logs.filter(action=action)
    if resource_type:
        audit_logs = audit_logs.filter(resource_type=resource_type)

    if not filters:
        return audit_logs

    search = (filters.get("search") or "").strip()
    filtered_action = (filters.get("action") or "").strip()
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    if search:
        audit_logs = audit_logs.filter(
            Q(user__email__icontains=search) | Q(description__icontains=search)
        )
    if filtered_action:
        audit_logs = audit_logs.filter(action=filtered_action)
    if start_date:
        audit_logs = audit_logs.filter(created_at__date__gte=start_date)
    if end_date:
        audit_logs = audit_logs.filter(created_at__date__lte=end_date)

    return audit_logs
