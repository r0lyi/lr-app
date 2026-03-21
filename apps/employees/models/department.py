"""Modelo de departamentos usado para agrupar empleados."""

from django.db import models


class Department(models.Model):
    """Representa un area organizativa con reglas basicas de ausencias."""

    name = models.CharField(max_length=100)
    max_concurrent_absences = models.IntegerField(default=1)

    class Meta:
        db_table = "department"
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"

    def __str__(self):
        """Devuelve el nombre legible del departamento."""

        return self.name
