"""Catalogo de estados por los que puede pasar una solicitud."""

from django.db import models


class VacationStatus(models.Model):
    """Representa un estado funcional del flujo de vacaciones."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "vacation_statuses"
        verbose_name = "Estado de vacaciones"
        verbose_name_plural = "Estados de vacaciones"

    def __str__(self):
        """Devuelve la etiqueta legible del estado."""

        return self.name
