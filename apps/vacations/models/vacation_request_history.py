"""Historico de cambios de estado aplicados a una solicitud."""

from django.conf import settings
from django.db import models

from apps.core.models import CreatedAtModel

from .vacation_request import VacationRequest
from .vacation_status import VacationStatus


class VacationRequestHistory(CreatedAtModel):
    """Guarda cada transicion de estado para trazabilidad del proceso."""

    vacation_request = models.ForeignKey(
        VacationRequest,
        on_delete=models.CASCADE,
        related_name="histories",
    )
    previous_status = models.ForeignKey(
        VacationStatus,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )
    new_status = models.ForeignKey(
        VacationStatus,
        on_delete=models.PROTECT,
        related_name="+",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacation_changes",
    )
    change_date = models.DateTimeField(auto_now_add = True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "vacation_request_histories"
        verbose_name = "Historial de solicitud"
        verbose_name_plural = "Historial de solicitudes"

    def __str__(self):
        """Resume el cambio de estado para listados simples."""

        return f"{self.vacation_request_id} | {self.previous_status} -> {self.new_status}"
