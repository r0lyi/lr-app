# Estructura del proyecto

## Vista general

El proyecto se organiza por dominios funcionales dentro de `apps/`. Cada dominio
agrupa su modelo, vistas, servicios, selectores, templates, static y tests.

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
├── doc/
├── docs/
├── static/
├── templates/
├── manage.py
├── pyproject.toml
└── uv.lock
```

La idea importante es esta:

- `apps/` contiene negocio.
- `templates/` y `static/` globales contienen piezas compartidas.
- `doc/` explica el producto y sus flujos.
- `docs/` define convenciones tecnicas y decisiones.
- `config/` arranca Django y conecta settings, URLs, ASGI y WSGI.

## Que contiene cada app

- `apps/users/`: usuario personalizado, DNI, roles, login, activacion, formularios y gestion admin de usuarios.
- `apps/employees/`: ficha `Employee`, departamentos, onboarding, perfil y panel del empleado.
- `apps/vacations/`: solicitudes de vacaciones, estados, validaciones, revision, eliminacion y exportacion.
- `apps/notifications/`: notificaciones internas para empleados, RRHH y administracion.
- `apps/audit/`: log de actividad, filtros de auditoria e historial de exportaciones.
- `apps/dashboard/`: shell autenticado, layout, navegacion y homes por rol.
- `apps/core/`: utilidades transversales, paginacion, decoradores, modelos base y helpers de presentacion.

## Patron interno recomendado

```text
apps/<dominio>/
├── admin.py
├── apps.py
├── forms.py
├── migrations/
├── models/
├── selectors/
├── services/
├── static/<dominio>/
├── templates/<dominio>/
├── tests/
├── urls.py
└── views/
```

No todas las apps tienen todas las carpetas, pero si una responsabilidad crece,
debe moverse al lugar correcto.

## Responsabilidad de cada capa

### `models/`

Define tablas, relaciones y restricciones de base de datos.

Ejemplos:

- `apps/users/models/user.py`: usuario personalizado con `email`, `dni`, token de activacion y roles.
- `apps/employees/models/employee.py`: ficha interna que conecta usuario con datos operativos.
- `apps/vacations/models/vacation_request.py`: solicitud de vacaciones y rango de fechas.

### `views/`

Reciben la peticion HTTP y orquestan el caso de uso.

Una vista puede:

- Validar formularios.
- Llamar a un servicio.
- Preparar contexto para un template.
- Redirigir o devolver errores.

Una vista no debe:

- Duplicar reglas de negocio.
- Construir consultas complejas que deban vivir en `selectors`.
- Registrar efectos secundarios sin pasar por el servicio adecuado cuando exista.

### `services/`

Ejecutan escritura y reglas de negocio.

Ejemplos:

- Crear una solicitud tras validar fechas, saldo y solapamientos.
- Revisar una solicitud desde RRHH y registrar auditoria.
- Crear un usuario pendiente de activacion.
- Generar un enlace de activacion.

### `selectors/`

Concentran lecturas y consultas ORM reutilizables.

Ejemplos:

- Obtener solicitudes filtradas para RRHH.
- Calcular contadores de dashboard.
- Preparar filas de usuarios para el panel admin.
- Consultar actividad visible del log.

### `templates/`

Cada app es dueña de sus templates de dominio.

Reglas clave:

- `pages/`: wrapper completo renderizado por una vista.
- `partials/`: fragmentos internos de una pantalla.
- `templates/components/`: componentes compartidos entre apps.
- Una app no debe incluir directamente templates privados de otra app.

Referencia: [`../docs/conventions/templates.md`](../docs/conventions/templates.md).

### `static/`

Se divide entre assets globales y assets de app.

- `static/`: foundations, layouts, componentes globales, branding y JS compartido.
- `apps/<app>/static/<app>/`: estilos o scripts propios de una pagina o flujo de esa app.

Referencia: [`../docs/conventions/static.md`](../docs/conventions/static.md).

## `dashboard` como shell, no como dueño de todo

`dashboard` sirve para:

- Resolver a que home va el usuario.
- Construir el layout autenticado.
- Renderizar navegacion por rol.
- Mostrar las homes de cada rol cuando actuan como entrada.

Pero las pantallas de dominio siguen perteneciendo a su app:

- Solicitar vacaciones vive en `apps/vacations/`.
- Perfil y onboarding viven en `apps/employees/`.
- Auditoria vive en `apps/audit/`.
- Gestion de usuarios vive en `apps/users/` aunque se vea dentro del panel admin.

Decision relacionada: [`../docs/adr/001-dashboard-ownership.md`](../docs/adr/001-dashboard-ownership.md).

## `doc/` y `docs/`

El proyecto usa dos carpetas porque tienen publicos distintos.

### `doc/`

Es la documentacion de onboarding:

- Explica flujos completos.
- Usa lenguaje didactico.
- Incluye listas de validaciones, efectos secundarios y ejemplos mentales.
- Esta pensada para leer antes de implementar.

### `docs/`

Es referencia tecnica:

- Convenciones de codigo.
- ADR.
- Estructura oficial.
- Reglas cortas para decidir donde poner un archivo.

Entrada tecnica: [`../docs/README.md`](../docs/README.md).

## Modelo mental simple

Si eres nuevo, piensa en el proyecto asi:

- `users` sabe quien eres y como entras.
- `employees` sabe tus datos internos como empleado.
- `vacations` sabe que vacaciones pides y como se revisan.
- `notifications` avisa a las personas correctas.
- `audit` registra que acciones importantes ocurrieron.
- `dashboard` te da una experiencia autenticada segun tu rol.
- `core` ofrece piezas compartidas para no repetir codigo.

## Regla practica antes de crear codigo

Antes de crear un archivo nuevo, hazte estas preguntas:

- Si escribe o valida negocio, debe ir a `services`.
- Si solo lee o prepara consultas, debe ir a `selectors`.
- Si recibe HTTP, debe ir a `views`.
- Si es UI compartida, debe ir a `templates/components/` o `static/`.
- Si es UI de una app, debe vivir dentro de esa app.
- Si cambia una decision de arquitectura, debe actualizar `docs/adr/`.
