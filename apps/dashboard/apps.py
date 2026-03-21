"""Configuracion declarativa de la app del dashboard."""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Registra metadatos del dashboard autenticado."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    verbose_name = "Dashboard"
