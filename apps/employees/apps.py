"""Configuracion declarativa de la app de empleados."""

from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    """Registra la app responsable de perfiles y departamentos."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.employees"
    verbose_name = "Empleados"
