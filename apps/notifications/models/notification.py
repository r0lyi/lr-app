"""Modelo de notificaciones visibles para cada usuario."""

from django.conf import settings
from django.db import models

from apps.core.models import CreatedAtModel


class Notification(CreatedAtModel):
    """Representa un mensaje enviado al inbox interno del usuario."""

    class Type(models.TextChoices):
        """Categorias soportadas por el inbox interno."""

        VACATION_INFO = ("info", "Mensaje general")
        VACATION_REQUEST_STATUS = (
            "vacation_request_status",
            "Cambio de estado de solicitud",
        )
        VACATION_REQUEST_SUBMISSION = (
            "vacation_request_submission",
            "Nueva solicitud enviada",
        )
        ADMIN_PERSONAL_MESSAGE = (
            "admin_personal_message",
            "Mensaje personal del administrador",
        )
        ADMIN_BROADCAST_MESSAGE = (
            "admin_broadcast_message",
            "Aviso general del administrador",
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_notifications",
        blank=True,
        null=True,
    )
    notification_type = models.CharField(
        max_length=40,
        choices=Type.choices,
        default=Type.VACATION_INFO,
    )
    title = models.CharField(max_length=140, blank=True, null=True)
    vacation_request = models.ForeignKey(
        "vacations.VacationRequest",
        on_delete=models.SET_NULL,
        related_name="notifications",
        blank=True,
        null=True,
    )
    previous_status_name = models.CharField(max_length=50, blank=True, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = "notifications"
        verbose_name = "Notificacion"
        verbose_name_plural = "Notificaciones"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(
                fields=["user", "is_read", "sent_at"],
                name="notif_user_read_sent_idx",
            )
        ]

    def __str__(self):
        """Resume el destinatario y el estado de lectura."""

        return f"Notificacion para {self.user} | leida: {self.is_read}"
