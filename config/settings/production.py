"""Overrides minimos de produccion sobre la configuracion comun."""

from .base import *  # noqa: F403
import os
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600
    )
}



DEBUG = False
ALLOWED_HOSTS = ['.onrender.com']
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
