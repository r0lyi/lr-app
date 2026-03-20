# Settings y configuracion Django

## Idea principal

Este proyecto no usa un unico `settings.py`. Usa una carpeta `config/settings/` para separar la configuracion comun de la configuracion especifica de cada entorno.

```text
config/settings/
├── __init__.py
├── base.py
├── local.py
├── production.py
└── test.py
```

## Por que esta estructura tiene sentido

Separar settings por entorno evita mezclar en un solo archivo cosas que cambian segun donde se ejecute la aplicacion.

### `base.py`

Contiene lo comun a todos los entornos:

- apps instaladas
- middleware
- templates
- modelo de usuario
- backends de autenticacion
- email
- cache
- validadores de contraseña
- archivos estaticos

### `local.py`

Contiene lo propio del desarrollo local:

- `DEBUG = True`
- `ALLOWED_HOSTS = ["*"]`
- conexion a PostgreSQL por variables de entorno
- `CSRF_TRUSTED_ORIGINS` de desarrollo

### `production.py`

Existe como lugar reservado para la configuracion de produccion, pero ahora mismo esta practicamente vacio y comentado. La estructura esta preparada, pero la configuracion de produccion todavia no esta terminada.

### `test.py`

Tambien existe como lugar reservado para settings de test, pero ahora mismo esta vacio.

## Como decide Django que settings cargar

El proyecto lee la variable `DJANGO_SETTINGS_MODULE`. Si no existe, por defecto usa `config.settings.local`.

Esto pasa en:

- `manage.py`
- `config/asgi.py`
- `config/wsgi.py`

Ejemplo simplificado:

```python
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    env("DJANGO_SETTINGS_MODULE", default="config.settings.local")
)
```

## Flujo real de carga

```text
Arranca Django
    -> lee .env
    -> busca DJANGO_SETTINGS_MODULE
    -> si no existe, usa config.settings.local
    -> local.py hace "from .base import *"
    -> Django ya tiene settings comunes + overrides locales
```

## Que configura `base.py`

## 1. Variables de entorno y ruta base

```python
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")
```

Esto hace dos cosas:

- `BASE_DIR` apunta a la raiz del proyecto.
- `.env` se carga automaticamente desde la raiz.

## 2. Seguridad basica

```python
SECRET_KEY = env("SECRET_KEY")
```

La clave secreta no esta hardcodeada en el repositorio. Se lee desde el entorno.

## 3. Apps instaladas

`base.py` separa apps de Django y apps del proyecto:

```python
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
```

Esto es util porque deja clara la diferencia entre framework y negocio.

## 4. Middleware

El proyecto usa el conjunto clasico de middleware de Django:

- seguridad
- sesiones
- middleware comun
- CSRF
- autenticacion
- mensajes
- proteccion contra clickjacking

En este flujo de auth son especialmente relevantes:

- `SessionMiddleware`: permite mantener la sesion del usuario autenticado.
- `CsrfViewMiddleware`: protege formularios POST.
- `AuthenticationMiddleware`: carga `request.user`.
- `MessageMiddleware`: permite mostrar mensajes de exito o error.

## 5. Templates

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

Esto significa:

- Django buscara templates globales en `templates/`
- tambien buscara templates dentro de cada app
- las vistas tendran acceso a `request`, `user` y `messages`

## 6. URLs raiz

```python
ROOT_URLCONF = "config.urls"
```

Django empieza resolviendo rutas desde `config/urls.py`.

## 7. Usuario personalizado

```python
AUTH_USER_MODEL = "users.User"
```

Esto es muy importante. El proyecto no usa el `User` por defecto de Django; usa uno propio definido en `apps/users/models/user.py`.

Gracias a esto se pueden guardar campos del dominio como:

- `dni`
- `activation_token`
- `token_expires_at`
- `registered_at`

## 8. Backends de autenticacion

```python
AUTHENTICATION_BACKENDS = [
    "apps.users.services.backends.DNIBackend",
    "django.contrib.auth.backends.ModelBackend",
]
```

Este punto explica por que el login funciona con DNI aunque el modelo de usuario use `email` como `USERNAME_FIELD`.

La autenticacion no depende solo de `USERNAME_FIELD`. Tambien depende de los backends registrados. Aqui el backend principal busca el usuario por `dni`.

## 9. Email

`base.py` centraliza la configuracion del envio de correos:

- `RESEND_API_KEY`
- `EMAIL_PROVIDER`
- `EMAIL_BACKEND`
- `EMAIL_TIMEOUT`
- `DEFAULT_FROM_EMAIL`
- `FRONTEND_URL`

`FRONTEND_URL` se usa para construir el enlace absoluto que llega por email.

## 10. Cache y rate limiting

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": env("LOCMEM_CACHE_LOCATION", default="lr-app-local"),
        "TIMEOUT": DEFAULT_CACHE_TIMEOUT,
    }
}
```

Y ademas define:

- `LOGIN_RATE_LIMIT_ATTEMPTS`
- `LOGIN_RATE_LIMIT_WINDOW`
- `ACTIVATION_RATE_LIMIT_ATTEMPTS`
- `ACTIVATION_RATE_LIMIT_WINDOW`

Esto se usa para limitar intentos de login y solicitudes de activacion.

## 11. Validadores de contraseña

El proyecto mantiene los validadores estandar de Django:

- similitud con atributos del usuario
- longitud minima
- contraseñas comunes
- contraseñas numericas

Esto afecta directamente al formulario de creacion de contraseña.

## 12. Internacionalizacion

Actualmente `base.py` define:

- `LANGUAGE_CODE = "en-us"`
- `TIME_ZONE = "UTC"`
- `USE_I18N = True`
- `USE_TZ = True`

Aunque la interfaz y los mensajes del proyecto estan escritos en español, la configuracion base de idioma y zona horaria sigue en valores por defecto de Django. Es importante saberlo porque puede afectar a fechas, formatos y expiraciones.

## 13. Archivos estaticos

```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

Esto hace que Django sirva CSS, JS e imagenes desde la carpeta `static/`.

## Que configura `local.py`

`local.py` hereda de `base.py`:

```python
from .base import *
```

Despues redefine lo propio del entorno local:

```python
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = ["*"]
```

Y define la base de datos PostgreSQL:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}
```

## Variables de entorno importantes

Estas son las mas relevantes para levantar el proyecto actual:

```env
SECRET_KEY=tu_clave
DJANGO_SETTINGS_MODULE=config.settings.local
DEBUG=True

DB_NAME=lr_app
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432

EMAIL_PROVIDER=console
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@example.com
FRONTEND_URL=http://localhost:8000
RESEND_API_KEY=

LOGIN_RATE_LIMIT_ATTEMPTS=5
LOGIN_RATE_LIMIT_WINDOW=900
ACTIVATION_RATE_LIMIT_ATTEMPTS=5
ACTIVATION_RATE_LIMIT_WINDOW=900
```

## Como encaja todo esto con el login por DNI

Para que ese flujo funcione hacen falta varias piezas de settings a la vez:

- `AUTH_USER_MODEL`: para usar el usuario custom con `dni` y token.
- `AUTHENTICATION_BACKENDS`: para que Django acepte DNI en el login.
- `EMAIL_*` y `FRONTEND_URL`: para enviar el enlace de activacion.
- `CACHES` y limites: para frenar intentos abusivos.
- `MessageMiddleware` y templates: para mostrar feedback al usuario.

## Idea simple para explicarselo a otra persona

`base.py` dice "esto siempre existe".

`local.py`, `production.py` y `test.py` dicen "esto cambia segun donde estoy corriendo".

Esa separacion hace que el proyecto sea mas mantenible, mas seguro y mas facil de desplegar.
