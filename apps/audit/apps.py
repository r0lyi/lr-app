"""Configuracion declarativa de la app de auditoria."""

from django.apps import AppConfig


class AuditConfig(AppConfig):
    """Registra la app que agrupa logs y exportaciones."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = "Auditoria"
