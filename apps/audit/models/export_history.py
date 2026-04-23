"""Modelo de historico de exportaciones generadas por usuarios."""

from django.conf import settings
from django.db import models

from apps.core.models import CreatedAtModel


class ExportHistory(CreatedAtModel):
    """Guarda metadatos de cada exportacion solicitada desde la aplicacion."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="export_histories",
    )
    file_name = models.CharField(max_length=255, blank=True, null=True)
    filters_json = models.JSONField(blank=True, null=True)
    rows_snapshot_json = models.JSONField(blank=True, null=True)
    columns_version = models.CharField(max_length=80, blank=True, null=True)
    total_records = models.IntegerField(blank=True, null=True)
    export_type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "export_histories"
        verbose_name = "Historial de exportacion"
        verbose_name_plural = "Historial de exportaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["export_type", "created_at"],
                name="export_type_created_idx",
            )
        ]

    def __str__(self):
        """Resume el tipo, estado y fecha de la exportacion."""

        return f"{self.export_type} | {self.status} | {self.created_at}"
