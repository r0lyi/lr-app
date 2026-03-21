"""Configuracion declarativa de la app de usuarios."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Registra la app que gestiona autenticacion y roles."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "Usuarios"
