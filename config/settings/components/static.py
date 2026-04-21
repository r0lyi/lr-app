"""Configuracion de static files."""

from .shared import BASE_DIR


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
