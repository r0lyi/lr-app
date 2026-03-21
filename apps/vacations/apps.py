"""Configuracion declarativa de la app de vacaciones."""

from django.apps import AppConfig


class VacationsConfig(AppConfig):
    """Registra la app del dominio de solicitudes de vacaciones."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vacations"
    verbose_name = "Vacaciones"
