"""Registro de apps instaladas en Django."""


DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    "apps.users",
    "apps.employees",
    "apps.vacations",
    "apps.notifications",
    "apps.audit",
    "apps.dashboard",
    "apps.core",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS
