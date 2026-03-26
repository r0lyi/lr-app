"""Modelo principal de solicitud de vacaciones realizada por un empleado."""

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel

from .vacation_status import VacationStatus


class VacationRequest(TimeStampedModel):
    """Representa una solicitud con rango de fechas y estado actual."""

    class ReprogramReason(models.TextChoices):
        """Motivos cerrados usados al reprogramar una solicitud."""

        IT = ("it", "IT")
        MATERNITY = ("maternity", "Maternidad")

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="vacation_requests",
    )
    status = models.ForeignKey(
        VacationStatus,
        on_delete=models.PROTECT,
        related_name="vacation_requests",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    requested_days = models.DecimalField(max_digits=6, decimal_places=2)
    request_date = models.DateTimeField(auto_now_add = True)
    resolution_date = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_vacation_requests",
    )
    employee_comment = models.TextField(blank=True, null=True)
    hr_comment = models.TextField(blank=True, null=True)
    reprogram_reason = models.CharField(
        max_length=20,
        choices=ReprogramReason.choices,
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "vacation_requests"
        verbose_name = "Solicitud de vacaciones"
        verbose_name_plural = "Solicitudes de vacaciones"
        indexes = [
            models.Index(
                fields=["employee", "start_date", "end_date"],
                name="vac_req_emp_dates_idx",
            ),
            models.Index(
                fields=["status", "request_date"],
                name="vac_req_status_req_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")),
                name="check_end_date_gte_start_date",
            )
        ]

    def __str__(self):
        """Resume empleado y rango pedido en los listados."""

        return f"{self.employee} | {self.start_date} -> {self.end_date}"
