"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import environ

from django.core.wsgi import get_wsgi_application

# Cargar .env
env = environ.Env()
environ.Env.read_env()

os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        env('DJANGO_SETTINGS_MODULE', default='config.settings.local')
    )
application = get_wsgi_application()
