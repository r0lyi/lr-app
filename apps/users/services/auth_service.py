"""Servicios puros del flujo de activacion, token y cambio de contraseña."""

import secrets
from datetime import timedelta
from typing import Literal

from django.utils import timezone
from django.utils.translation import gettext as _

from apps.users.models import User

from .email import send_activation_email

TokenStatus = Literal["valid", "expired", "invalid"]


def request_activation(
    dni: str,
    *,
    activation_url_base: str | None = None,
) -> tuple[bool, str]:
    """Genera un token temporal y envia el email si el DNI existe."""

    try:
        user = User.objects.get(dni=dni)
    except User.DoesNotExist:
        # La respuesta no revela si el usuario existe para evitar enumeracion.
        return False, _("Si el DNI es correcto, recibirás un email.")

    token = secrets.token_urlsafe(32)

    user.activation_token = token
    user.token_expires_at = timezone.now() + timedelta(hours=24)
    user.save(update_fields=["activation_token", "token_expires_at"])

    send_activation_email(
        user.email,
        token,
        activation_url_base=activation_url_base,
    )

    return True, _("Si el DNI es correcto, recibirás un email.")


def resolve_token(token: str) -> tuple[User | None, TokenStatus]:
    """Devuelve el usuario si el token sigue vigente y el estado detectado."""

    try:
        user = User.objects.get(activation_token=token)
    except User.DoesNotExist:
        return None, "invalid"

    if user.token_expires_at and user.token_expires_at > timezone.now():
        return user, "valid"

    return None, "expired"


def validate_token(token: str) -> User | None:
    """Mantiene compatibilidad devolviendo solo el usuario vigente."""

    user, _status = resolve_token(token)
    return user


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

    from apps.audit.services import log_user_account_activated

    log_user_account_activated(user=user)
