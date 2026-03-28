"""Selectores de lectura para el historial de auditoria."""

from apps.audit.models import AuditLog


def get_audit_logs(*, action=None, resource_type=None, limit=None):
    """Devuelve el historial de auditoria listo para pintar en pantalla."""

    audit_logs = AuditLog.objects.select_related("user").order_by("-created_at")

    if action:
        audit_logs = audit_logs.filter(action=action)
    if resource_type:
        audit_logs = audit_logs.filter(resource_type=resource_type)
    if limit is not None:
        audit_logs = audit_logs[:limit]

    return audit_logs
