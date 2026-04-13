"""Servicios puros del flujo de activacion, token y cambio de contraseña."""

import secrets
from datetime import timedelta

from django.utils import timezone

from apps.users.models import User

from .email import send_activation_email


def request_activation(dni: str) -> tuple[bool, str]:
    """Genera un token temporal y envia el email si el DNI existe."""

    try:
        user = User.objects.get(dni=dni)
    except User.DoesNotExist:
        # La respuesta no revela si el usuario existe para evitar enumeracion.
        return False, "Si el DNI es correcto, recibirás un email."

    token = secrets.token_urlsafe(32)

    user.activation_token = token
    user.token_expires_at = timezone.now() + timedelta(hours=24)
    user.save(update_fields=["activation_token", "token_expires_at"])

    send_activation_email(user.email, token)

    return True, "Si el DNI es correcto, recibirás un email."


def validate_token(token: str) -> User | None:
    """Devuelve el usuario asociado a un token vigente o `None`."""

    try:
        return User.objects.get(
            activation_token=token,
            token_expires_at__gt=timezone.now(),
        )
    except User.DoesNotExist:
        return None


def set_password(user: User, password: str) -> None:
    """Activa la cuenta, guarda la contraseña e invalida el token usado."""

    user.set_password(password)
    user.is_active = True
    user.registered_at = timezone.now()
    user.activation_token = None
    user.token_expires_at = None
    user.save(
        update_fields=[
            "password",
            "is_active",
            "registered_at",
            "activation_token",
            "token_expires_at",
        ]
    )
