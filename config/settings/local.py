"""Settings locales usados por defecto en desarrollo."""

from .base import *

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME_LOCAL"),
        "USER": env("DB_USER_LOCAL"),
        "PASSWORD": env("DB_PASSWORD_LOCAL"),
        "HOST": env("DB_HOST_LOCAL"),
        "PORT": env("DB_PORT_LOCAL"),
    }
}

# En local confiamos en los orígenes típicos del backend Django.
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:8000", "http://127.0.0.1:8000"],
)
