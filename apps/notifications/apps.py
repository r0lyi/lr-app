"""Configuracion declarativa de la app de notificaciones."""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Registra la app del inbox interno del usuario."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    verbose_name = "Notificaciones"
