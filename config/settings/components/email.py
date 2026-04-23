"""Parametros de email y proveedor de entrega."""

from .shared import env


RESEND_API_KEY = env("RESEND_API_KEY", default="").strip()
EMAIL_PROVIDER = env("EMAIL_PROVIDER", default="console").strip().lower()
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", default=15)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:8000")
