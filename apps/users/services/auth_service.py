import secrets
from datetime import timedelta
from django.utils import timezone
from apps.users.models import User
from .email_service import send_activation_email



# Servicios relacionados con autenticación, activación de cuenta y gestión de tokens
def request_activation(dni: str) -> tuple[bool, str]:
    """
    Busca el usuario por DNI, genera token y envía email.
    Retorna (éxito, mensaje)
    """
    try:
        user = User.objects.get(dni=dni)
    except User.DoesNotExist:
        # Mensaje genérico — no revelar si el DNI existe o no
        return False, "Si el DNI es correcto, recibirás un email."

    # Genera token seguro
    token = secrets.token_urlsafe(32)

    # Guarda token con expiración de 24h
    user.activation_token = token
    user.token_expires_at = timezone.now() + timedelta(hours=24)
    user.save(update_fields=["activation_token", "token_expires_at"])

    send_activation_email(user.email, token)

    return True, "Si el DNI es correcto, recibirás un email."



# Valida el token de activación, retorna el usuario o None
def validate_token(token: str) -> User | None:
    """
    Valida que el token existe y no ha expirado.
    Retorna el User o None.
    """
    try:
        user = User.objects.get(
            activation_token=token,
            token_expires_at__gt=timezone.now(),
        )
        return user
    except User.DoesNotExist:
        return None


# Establece la contraseña, activa el usuario e invalida el token
def set_password(user: User, password: str) -> None:
    """
    Hashea y guarda la contraseña, activa el usuario, invalida el token.
    """
    user.set_password(password)
    user.is_active = True
    user.registered_at = timezone.now()
    user.activation_token = None
    user.token_expires_at = None
    user.save(update_fields=[
        "password",
        "is_active",
        "registered_at",
        "activation_token",
        "token_expires_at",
    ])