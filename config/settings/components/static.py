"""Configuracion de static files y directorios de salida locales."""

from .shared import BASE_DIR


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
EXPORTS_ROOT = BASE_DIR / "var" / "exports"
