# Project Structure

## Objetivo

El proyecto se organiza por dominio funcional. Cada app debe ser propietaria de
su modelo, casos de uso, consultas, templates y assets especificos.

Esta estructura evita que `dashboard` o `core` se conviertan en carpetas donde
todo acaba mezclado.

## Carpetas raiz

```text
lr-app/
  apps/
  config/
  doc/
  docs/
  static/
  templates/
  var/
```

Responsabilidades:

- `apps/`: dominios Django del producto.
- `config/`: settings, URLs raiz, ASGI/WSGI.
- `doc/`: guias de onboarding y flujos funcionales.
- `docs/`: referencia tecnica, convenciones y ADR.
- `static/`: CSS, JS, imagenes y componentes visuales compartidos.
- `templates/`: layouts y componentes HTML compartidos.
- `var/`: archivos generados en runtime, como exportaciones.

## Apps actuales

### `apps/users`

Responsable de:

- Usuario personalizado.
- DNI.
- Login y activacion.
- Roles funcionales.
- Gestion administrativa de usuarios.

### `apps/employees`

Responsable de:

- Ficha de empleado.
- Onboarding/post-login.
- Perfil.
- Fecha de ingreso.
- Departamentos a nivel interno.

Departamentos no se muestran en la interfaz principal actual, pero se conservan
en modelo y Django Admin para futuras versiones.

### `apps/vacations`

Responsable de:

- Solicitudes de vacaciones.
- Estados.
- Validaciones de solicitud.
- Revision RRHH/admin.
- Alertas previas a exportacion.
- Exportacion a Excel.

### `apps/notifications`

Responsable de:

- Notificaciones internas.
- Avisos a RRHH.
- Avisos al empleado cuando cambia una solicitud.

### `apps/audit`

Responsable de:

- Historial de actividad.
- Historial de exportaciones.
- Selectors y filtros de auditoria.

### `apps/dashboard`

Responsable de:

- Shell autenticado.
- Header.
- Sidebar.
- Homes por rol.
- Navegacion principal.

No debe ser propietario de pantallas de dominio como solicitudes, perfil o
historial. Esas pantallas viven en su app funcional.

### `apps/core`

Responsable de:

- Utilidades transversales.
- Decoradores compartidos.
- Paginacion.
- Helpers de presentacion.
- Branding del Django Admin cuando aplica.

## Estructura interna recomendada por app

```text
apps/<app>/
  admin.py
  forms/
  models/
  selectors/
  services/
  static/<app>/
  templates/<app>/
  tests/
  urls.py
  views/
```

No todas las apps necesitan todas las carpetas, pero si una app crece debe
seguir este modelo.

## Capas

### `models`

Define estructura de datos y relaciones.

Debe contener:

- Campos.
- Relaciones.
- Metodos simples del modelo.
- Constraints si son propios de base de datos.

No debe contener:

- Flujos completos de negocio.
- Envio de emails.
- Logica HTTP.

### `views`

Orquesta peticiones HTTP.

Debe contener:

- Permisos/decoradores.
- Formularios.
- Llamadas a servicios/selectors.
- Contexto para templates.
- Mensajes y redirecciones.

### `services`

Ejecuta casos de uso y validaciones de escritura.

Ejemplos:

- Crear solicitud de vacaciones.
- Revisar solicitud.
- Crear usuario desde admin.
- Cambiar rol principal.
- Registrar exportacion.

### `selectors`

Centraliza queries de lectura.

Ejemplos:

- Buscar solicitudes solapadas.
- Sumar dias reservados.
- Filtrar historial de actividad.
- Listar exportaciones.

### `templates`

Cada app renderiza sus propias paginas.

Patron:

- `pages/`: wrappers renderizados por vistas.
- `partials/`: piezas internas de una pantalla o feature.

### `static`

Cada app mantiene CSS/JS especifico en su carpeta local. Lo compartido vive en
`static/` raiz.

## Relacion entre `doc/` y `docs/`

`doc/` responde:

- Que hace el producto.
- Como funciona un flujo.
- Que validaciones se aplican.
- Que debe saber una persona nueva.

`docs/` responde:

- Donde escribir codigo.
- Que convencion seguir.
- Que decision arquitectonica esta vigente.
- Que patron se debe respetar.

Ver ADR:

- [`../adr/004-documentation-structure.md`](../adr/004-documentation-structure.md)

## Regla antes de crear archivos

Antes de crear un archivo nuevo, confirmar:

- Que app es duena del dominio.
- Si es lectura, va en `selectors`.
- Si escribe o valida negocio, va en `services`.
- Si es pantalla completa, va en `templates/<app>/pages/`.
- Si es fragmento local, va en `templates/<app>/partials/`.
- Si es componente compartido, va en `templates/components/`.
- Si el CSS/JS se comparte, va en `static/`.
- Si el CSS/JS es especifico, va en `apps/<app>/static/<app>/`.
