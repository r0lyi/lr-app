"""Punto de ensamblado de settings compartidos del proyecto."""

from .components.apps import INSTALLED_APPS
from .components.auth import AUTHENTICATION_BACKENDS, AUTH_PASSWORD_VALIDATORS
from .components.auth import AUTH_USER_MODEL
from .components.cache import (
    ACTIVATION_RATE_LIMIT_ATTEMPTS,
    ACTIVATION_RATE_LIMIT_WINDOW,
    CACHES,
    DEFAULT_CACHE_TIMEOUT,
    LOGIN_RATE_LIMIT_ATTEMPTS,
    LOGIN_RATE_LIMIT_WINDOW,
)
from .components.email import (
    DEFAULT_FROM_EMAIL,
    EMAIL_BACKEND,
    EMAIL_PROVIDER,
    EMAIL_TIMEOUT,
    FRONTEND_URL,
    RESEND_API_KEY,
)
from .components.i18n import LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_TZ
from .components.middleware import MIDDLEWARE
from .components.shared import BASE_DIR, SECRET_KEY, env
from .components.static import STATICFILES_DIRS, STATIC_URL
from .components.templates import TEMPLATES


ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
