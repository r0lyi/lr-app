"""Modelo de eventos auditables ejecutados por usuarios del sistema."""

from django.conf import settings
from django.db import models

from apps.core.models import CreatedAtModel


class AuditLog(CreatedAtModel):
    """Registra una accion concreta sobre un recurso de negocio."""

    ACTION_LABELS = {
        "user_created": "Usuario creado",
        "user_primary_role_changed": "Cambio de rol",
        "user_access_state_changed": "Cambio de acceso",
        "user_department_changed": "Cambio de departamento",
        "user_profile_updated": "Datos de usuario",
        "user_password_changed": "Contraseña actualizada",
        "user_account_activated": "Cuenta activada",
        "vacation_request_reviewed": "Solicitud editada",
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=50)
    resource_id = models.BigIntegerField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "audit_logs"
        verbose_name = "Log de auditoria"
        verbose_name_plural = "Logs de auditoria"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["resource_type", "resource_id", "created_at"],
                name="audit_resource_created_idx",
            )
        ]

    def __str__(self):
        """Resume el evento para listados de admin y debugging."""

        return f"{self.action} | {self.resource_type}:{self.resource_id}"

    @property
    def action_label(self):
        """Devuelve una etiqueta legible para la accion registrada."""

        return self.ACTION_LABELS.get(self.action, "Actividad del sistema")
