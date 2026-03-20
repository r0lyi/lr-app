# LR App

Aplicacion web desarrollada con Django para la gestion interna de vacaciones, empleados, notificaciones y auditoria. El proyecto usa un usuario personalizado, autenticacion por DNI y un flujo de creacion o recuperacion de contrasena mediante email con token temporal.

## Vision general

`lr-app` esta organizado por dominios dentro de `apps/`, de modo que cada modulo del negocio mantiene sus modelos, vistas, servicios, templates y tests cerca unos de otros.

Actualmente el proyecto ya incluye:

- autenticacion con `DNI + contrasena`
- activacion o recuperacion de acceso por email
- usuario personalizado con roles
- dashboard autenticado
- modulos base para empleados, vacaciones, notificaciones y auditoria
- documentacion tecnica en `/doc/`

## Stack tecnologico

- Python 3.12+
- Django 6
- PostgreSQL
- `django-environ` para variables de entorno
- `psycopg` para conexion con PostgreSQL
- Resend o backend de email de Django para correos
- HTMX para interacciones ligeras en formularios de autenticacion

## Estructura principal

```text
lr-app/
├── apps/
│   ├── audit/
│   ├── core/
│   ├── dashboard/
│   ├── employees/
│   ├── notifications/
│   ├── users/
│   └── vacations/
├── config/
│   ├── settings/
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── doc/
├── static/
├── templates/
├── manage.py
├── pyproject.toml
└── uv.lock
```

## Modulos principales

- `apps/users/`: autenticacion, usuario personalizado, roles, validacion de DNI, backend custom, emails y vistas de acceso.
- `apps/employees/`: perfil de empleado y departamentos.
- `apps/vacations/`: solicitudes de vacaciones y estados.
- `apps/notifications/`: notificaciones de usuario.
- `apps/audit/`: logs de auditoria e historial de exportaciones.
- `apps/dashboard/`: zona autenticada inicial despues del login.
- `apps/core/`: modelos base, decoradores y utilidades compartidas.

## Flujo de autenticacion

El acceso al sistema funciona asi:

1. Se crea un usuario con `email` y `dni`.
2. Si el usuario aun no tiene contrasena, o necesita recuperarla, solicita un enlace desde `/auth/activate/`.
3. El sistema genera un token temporal de 24 horas y envia un email.
4. El usuario accede a `/auth/set-password/<token>/` y define una nueva contrasena.
5. La cuenta se activa y el usuario ya puede entrar desde `/auth/login/` con `DNI + contrasena`.

Piezas tecnicas clave:

- modelo custom: `apps.users.models.User`
- backend de auth por DNI: `apps.users.services.backends.DNIBackend`
- servicio de activacion: `apps.users.services.auth_service`
- email de activacion: `apps.users.services.email_service`
- vistas de acceso: `apps.users.views.auth_views`

## Requisitos previos

Antes de ejecutar el proyecto necesitas:

- Python `>= 3.12`
- PostgreSQL disponible
- archivo `.env` en la raiz del proyecto
- `uv` instalado para gestionar entorno y dependencias

## Instalacion y arranque local

### 1. Instalar dependencias

```bash
uv sync
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la raiz del proyecto con una configuracion parecida a esta:

```env
SECRET_KEY=tu_clave_secreta
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

### 3. Aplicar migraciones

```bash
uv run python manage.py migrate
```

### 4. Ejecutar el servidor

```bash
uv run python manage.py runserver
```

La aplicacion quedara disponible, por defecto, en:

```text
http://127.0.0.1:8000/
```

## Rutas principales

- `/`: redirige al dashboard si hay sesion o al login si no la hay
- `/auth/login/`: login con DNI y contrasena
- `/auth/activate/`: solicitud de enlace para crear o recuperar contrasena
- `/auth/set-password/<token>/`: definicion de contrasena mediante token
- `/dashboard/`: pantalla autenticada principal
- `/admin/`: panel de administracion Django

## Settings y entornos

La configuracion Django esta separada en:

- `config/settings/base.py`: configuracion comun
- `config/settings/local.py`: desarrollo local
- `config/settings/production.py`: reservado para produccion
- `config/settings/test.py`: reservado para tests

Si no se define `DJANGO_SETTINGS_MODULE`, el proyecto arranca por defecto con:

```text
config.settings.local
```

## Tests

Para ejecutar el test del flujo principal de autenticacion:

```bash
uv run python manage.py test apps.users.tests.test_auth_flow
```

## Documentacion

La documentacion detallada del proyecto vive en [`doc/`](./doc/README.md).

Guias disponibles:

- [`doc/README.md`](./doc/README.md): indice general de documentacion
- [`doc/01-estructura-del-proyecto.md`](./doc/01-estructura-del-proyecto.md): estructura de carpetas y organizacion por apps
- [`doc/02-settings-y-configuracion-django.md`](./doc/02-settings-y-configuracion-django.md): settings, entornos y configuracion base de Django
- [`doc/03-flujo-auth-login-dni.md`](./doc/03-flujo-auth-login-dni.md): flujo tecnico completo del login por DNI y activacion por email

## Estado actual

El proyecto ya tiene base solida para autenticacion y estructura de dominio, pero hay dos puntos a tener en cuenta:

- `config/settings/production.py` aun no esta completado
- `config/settings/test.py` existe como lugar preparado para crecer, pero todavia no tiene configuracion propia

## Comandos utiles

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
uv run python manage.py test
```

## Resumen

Este repositorio esta pensado como una base de aplicacion interna en Django, con separacion clara por dominios, autenticacion personalizada y una documentacion que permite a otro desarrollador entender rapido tanto la arquitectura general como el flujo de acceso.
