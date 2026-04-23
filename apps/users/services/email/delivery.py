"""Compatibilidad temporal hacia la capa de email reorganizada."""

from apps.users.services.email_service import send_activation_email, send_email_message

__all__ = ["send_activation_email", "send_email_message"]
