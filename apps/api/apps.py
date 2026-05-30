"""Configuracion declarativa de la app de API interna."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Registra la capa API sin mezclarla con dominios de negocio."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    verbose_name = "API interna"
