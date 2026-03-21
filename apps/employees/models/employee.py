"""Modelo del perfil interno que completa el onboarding del empleado."""

from django.conf import settings
from django.db import models

from apps.core.models import CreatedAtModel

from .department import Department


class Employee(CreatedAtModel):
    """Amplia al usuario autenticado con datos operativos de RRHH."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    hire_date = models.DateField()
    available_days = models.IntegerField(default=0)
    taken_days = models.IntegerField(default=0)

    class Meta:
        db_table = "employee"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"

    def __str__(self):
        """Devuelve el nombre completo mostrado en paneles y admin."""

        return f"{self.first_name} {self.last_name}"
