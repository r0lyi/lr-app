"""Configuracion regional compartida."""


from config.settings.components.shared import BASE_DIR


LANGUAGE_CODE = "es"

LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
    ('cat', 'Català'),
]
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
