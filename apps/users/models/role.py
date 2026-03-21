"""Modelos de roles disponibles para clasificar a los usuarios del sistema."""

from django.db import models


class Role(models.Model):
    """Catalogo simple de roles: employee, rrhh y admin."""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "roles"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name
