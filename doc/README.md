# Documentacion del proyecto `lr-app`

Esta carpeta es la puerta de entrada para entender el proyecto sin tener que leer
todo el codigo desde cero. Esta escrita en español claro y pensada para que un
desarrollador junior pueda construir un mapa mental antes de tocar una vista,
un servicio o una consulta.

## `doc/` y `docs/`: cual leer y para que

El proyecto mantiene dos capas de documentacion:

- `doc/`: guias largas de onboarding, flujos funcionales y explicaciones paso a paso.
- `docs/`: referencia tecnica compacta, convenciones y decisiones de arquitectura.

Regla sencilla:

- Si quieres entender como funciona el producto, empieza por `doc/`.
- Si vas a escribir codigo y necesitas una regla concreta, consulta `docs/`.
- Si hay una decision arquitectonica importante, debe quedar explicada en `docs/adr/`.

Indice tecnico relacionado:

- [`../docs/README.md`](../docs/README.md): entrada de referencia tecnica.
- [`../docs/architecture/project_structure.md`](../docs/architecture/project_structure.md): estructura oficial.
- [`../docs/conventions/services.md`](../docs/conventions/services.md): reglas para `views`, `services` y `selectors`.
- [`../docs/conventions/templates.md`](../docs/conventions/templates.md): ownership de templates.
- [`../docs/conventions/static.md`](../docs/conventions/static.md): ownership de CSS, JS e imagenes.

## Guias de onboarding

- [`01-estructura-del-proyecto.md`](./01-estructura-del-proyecto.md): carpetas, apps y modelo mental del repositorio.
- [`02-settings-y-configuracion-django.md`](./02-settings-y-configuracion-django.md): settings por entorno, auth, email y configuracion base.
- [`03-flujo-auth-login-dni.md`](./03-flujo-auth-login-dni.md): login con DNI, activacion por email, token y contraseña.
- [`04-flujo-roles-y-post-login.md`](./04-flujo-roles-y-post-login.md): roles, dispatcher de dashboard, onboarding y permisos.
- [`05-flujo-solicitudes-vacaciones.md`](./05-flujo-solicitudes-vacaciones.md): validaciones antes de crear una solicitud de vacaciones.
- [`06-rrhh-alertas-exportaciones.md`](./06-rrhh-alertas-exportaciones.md): alertas de RRHH, solapamientos e historial de exportaciones.
- [`07-auditoria-y-admin-django.md`](./07-auditoria-y-admin-django.md): log de actividad y administracion completa desde Django Admin.

## Resumen rapido del stack

- Backend: Django 6.
- Base de datos: PostgreSQL.
- Variables de entorno: `django-environ`.
- Email: backend de Django o Resend.
- Autenticacion: usuario personalizado, login con DNI y activacion por token.
- UI: templates Django, CSS propio, componentes compartidos y JavaScript puntual.
- Exportaciones: archivos generados en `var/exports/`, fuera del codigo versionado.

## Modulos principales

- `apps/users/`: usuario personalizado, roles, DNI, activacion, login y gestion admin de usuarios.
- `apps/employees/`: ficha interna de empleado, onboarding, perfil y departamentos.
- `apps/vacations/`: solicitudes, estados, validaciones, revision RRHH y exportacion.
- `apps/notifications/`: inbox interno, avisos de solicitudes y mensajes admin.
- `apps/audit/`: log de actividad e historial de exportaciones.
- `apps/dashboard/`: shell autenticado, navegacion y homes por rol.
- `apps/core/`: utilidades transversales, decoradores, paginacion y presentacion compartida.

## Ruta de lectura recomendada

1. Lee [`01-estructura-del-proyecto.md`](./01-estructura-del-proyecto.md).
2. Revisa [`03-flujo-auth-login-dni.md`](./03-flujo-auth-login-dni.md).
3. Continua con [`04-flujo-roles-y-post-login.md`](./04-flujo-roles-y-post-login.md).
4. Si vas a tocar vacaciones, lee [`05-flujo-solicitudes-vacaciones.md`](./05-flujo-solicitudes-vacaciones.md).
5. Si vas a tocar RRHH/exportaciones, lee [`06-rrhh-alertas-exportaciones.md`](./06-rrhh-alertas-exportaciones.md).
6. Si vas a tocar permisos, trazabilidad o soporte interno, lee [`07-auditoria-y-admin-django.md`](./07-auditoria-y-admin-django.md).
7. Antes de crear archivos nuevos, consulta las convenciones en [`../docs/README.md`](../docs/README.md).

## Comandos utiles

```bash
uv run python manage.py migrate
uv run python manage.py runserver
uv run python manage.py test
uv run python manage.py check
```

Para tests enfocados:

```bash
uv run python manage.py test apps.users.tests.test_auth_flow
uv run python manage.py test apps.vacations.tests
uv run python manage.py test apps.audit.tests
```

## Principio de mantenimiento

Cuando cambie una regla de negocio, la documentacion debe actualizarse en dos
niveles:

- La guia de `doc/` que explica el flujo a una persona nueva.
- La convencion o ADR de `docs/` si el cambio afecta arquitectura, ownership o patron de codigo.
