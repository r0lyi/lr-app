from .base import *

# Local settings para desarrollo y pruebas
DEBUG = env.bool('DEBUG', default=True)

# Allowed hosts para desarrollo y pruebas
ALLOWED_HOSTS = ["*"]
# CORS configuration para permitir solicitudes desde el frontend en desarrollo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

# CORS configuration para permitir solicitudes desde el frontend en desarrollo
CSRF_TRUSTED_ORIGINS = env.list(
    'CSRF_TRUSTED_ORIGINS',
    default=['http://localhost:8000', 'http://127.0.0.1:8000',]
)