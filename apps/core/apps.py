"""Configuracion de la app de utilidades compartidas."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Registra la app que contiene utilidades y modelos base."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"
