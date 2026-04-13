"""Configuracion de cache y rate limiting basico."""

from .shared import env


DEFAULT_CACHE_TIMEOUT = env.int("CACHE_TIMEOUT", default=300)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": env("LOCMEM_CACHE_LOCATION", default="lr-app-local"),
        "TIMEOUT": DEFAULT_CACHE_TIMEOUT,
    }
}

LOGIN_RATE_LIMIT_ATTEMPTS = env.int("LOGIN_RATE_LIMIT_ATTEMPTS", default=5)
LOGIN_RATE_LIMIT_WINDOW = env.int("LOGIN_RATE_LIMIT_WINDOW", default=900)
ACTIVATION_RATE_LIMIT_ATTEMPTS = env.int(
    "ACTIVATION_RATE_LIMIT_ATTEMPTS",
    default=5,
)
ACTIVATION_RATE_LIMIT_WINDOW = env.int(
    "ACTIVATION_RATE_LIMIT_WINDOW",
    default=900,
)
