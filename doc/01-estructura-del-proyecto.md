# Estructura del proyecto

## Vista general

Este proyecto sigue una organizacion por dominios dentro de `apps/`. La idea es que cada modulo del negocio tenga su propia carpeta y que dentro de ella viva todo lo necesario: modelos, vistas, servicios, tests, templates y URLs.

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
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── static/
├── templates/
├── manage.py
├── pyproject.toml
└── uv.lock
```

## Que significa cada carpeta raiz

### `apps/`

Es el corazon funcional del proyecto. Cada subcarpeta representa una parte del negocio.

- `apps/users/`: usuario personalizado, roles, validacion de DNI, email de activacion, backend de autenticacion por DNI y vistas de login.
- `apps/employees/`: perfil de empleado y departamentos.
- `apps/vacations/`: solicitudes de vacaciones y sus estados.
- `apps/notifications/`: notificaciones para usuarios.
- `apps/audit/`: logs de auditoria e historial de exportaciones.
- `apps/dashboard/`: landing autenticada despues del login.
- `apps/core/`: piezas compartidas entre apps, como modelos base, decoradores y utilidades de rate limit.

### `config/`

Contiene la configuracion global de Django.

- `config/urls.py`: define las rutas raiz del sitio.
- `config/settings/`: separa settings comunes y settings por entorno.
- `config/asgi.py` y `config/wsgi.py`: puntos de entrada para servir la aplicacion.

### `templates/`

Templates globales compartidos. En este proyecto se usan sobre todo para:

- `templates/base.html`: layout base.
- `templates/components/`: componentes reutilizables, como toasts y campos de formulario.
- `templates/emails/`: emails HTML y texto plano.

### `static/`

Activos globales del frontend.

- `static/css/foundation/`: estilos base y tokens visuales.
- `static/css/components/`: botones, formularios, modales, toasts.
- `static/css/layout/`: helpers de layout.
- `static/css/pages/`: CSS especifico de paginas, por ejemplo auth.
- `static/js/`: JavaScript global, como el manejo de toasts.
- `static/images/`: logos e iconos.

### Archivos de raiz

- `manage.py`: ejecuta comandos de Django.
- `pyproject.toml`: dependencias del proyecto.
- `uv.lock`: lockfile del entorno.
- `main.py`: no forma parte del flujo normal de Django; parece un archivo generado por plantilla inicial.

## Patron interno de cada app

Aunque algunas carpetas aun estan vacias o preparadas para crecer, el patron general ya se ve claro:

```text
apps/<dominio>/
├── admin.py
├── apps.py
├── migrations/
├── models/
├── selectors/
├── services/
├── templates/
├── tests/
├── views/
└── urls.py
```

## Para que sirve cada tipo de carpeta

### `models/`

Define las tablas y relaciones de base de datos.

Ejemplo:

- `apps/users/models/user.py`: define el usuario personalizado.
- `apps/employees/models/employee.py`: relaciona un usuario con su perfil de empleado.

### `views/`

Reciben la peticion HTTP, validan formularios, llaman a servicios y devuelven la respuesta.

Ejemplo:

- `apps/users/views/auth_views.py`: login, logout, activacion y establecimiento de contraseña.

### `services/`

Contienen la logica de negocio para no cargar demasiado las vistas.

Ejemplo:

- `apps/users/services/auth_service.py`: genera tokens, valida vencimientos y guarda contraseñas.
- `apps/users/services/email_service.py`: construye y envia el email de activacion.
- `apps/core/utils/rate_limits.py`: controla intentos de login y activacion.

### `selectors/`

La idea de esta carpeta es centralizar lecturas complejas o consultas reutilizables. En este repositorio muchos `selectors/` estan preparados pero todavia no tienen implementacion real. Aun asi, la estructura ya deja claro que el proyecto quiere separar:

- escritura y reglas de negocio en `services/`
- lectura especializada en `selectors/`

### `templates/`

Cada app puede tener sus propias vistas HTML.

Ejemplo:

- `apps/users/templates/users/login.html`
- `apps/users/templates/users/request_activation.html`
- `apps/users/templates/users/set_password.html`

### `tests/`

Los tests viven junto al dominio al que pertenecen.

Ejemplo:

- `apps/users/tests/test_auth_flow.py`: prueba el flujo completo de activacion y login.

## Por que esta estructura es util

### 1. Reduce el acoplamiento

La logica del login no esta mezclada con vacaciones, notificaciones o auditoria.

### 2. Hace mas facil crecer

Si mas adelante `employees` o `vacations` necesitan servicios, vistas, APIs o consultas complejas, ya existe un lugar claro donde poner cada cosa.

### 3. Facilita el onboarding

Un desarrollador nuevo puede entrar en `apps/users/` y encontrar casi todo lo relacionado con autenticacion sin navegar por medio proyecto.

### 4. Ayuda a mantener vistas delgadas

La vista se ocupa de HTTP; el servicio se ocupa de la regla de negocio.

## Como se reparte el flujo de autenticacion dentro del proyecto

El auth no vive en un solo archivo. Esta distribuido intencionalmente:

- `apps/users/models/user.py`: define el usuario y los campos del token.
- `apps/users/forms.py`: valida el DNI y las contraseñas.
- `apps/users/services/validators.py`: normaliza y valida el DNI.
- `apps/users/services/backends.py`: permite autenticar usando DNI.
- `apps/users/services/auth_service.py`: genera y valida tokens; activa cuentas.
- `apps/users/services/email_service.py`: crea y envia el correo.
- `apps/users/views/auth_views.py`: orquesta la peticion HTTP.
- `apps/users/urls.py`: expone las rutas.
- `apps/users/templates/users/*.html`: presenta la UI del login y activacion.
- `templates/emails/*`: contenido del email de activacion.
- `apps/users/tests/test_auth_flow.py`: comprueba el flujo completo.

## Modelo mental simple

Si se lo explicas a una persona nueva, esta es una buena forma:

- `config/` dice a Django como arrancar.
- `apps/` dice que sabe hacer el negocio.
- `templates/` dice como se ve.
- `static/` dice como se estiliza y que scripts usa.
- `tests/` comprueban que todo eso sigue funcionando.
