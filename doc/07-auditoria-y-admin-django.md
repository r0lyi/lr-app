# Auditoria y Django Admin

Esta guia explica que acciones quedan registradas en el historial de actividad y
que alcance tiene el Django Admin como herramienta interna de gestion completa.

## Objetivo

El sistema gestiona vacaciones, usuarios y permisos. Por eso necesita trazabilidad
clara:

- Quien hizo el cambio.
- Sobre que usuario o solicitud se hizo.
- Que cambio exactamente.
- Cuando ocurrio.

La auditoria no reemplaza validaciones ni permisos. Es una capa de transparencia
para soporte, RRHH y administracion.

## Archivos principales

- `apps/audit/models/audit_log.py`: modelo del historial de actividad.
- `apps/audit/services/audit_logs.py`: funciones para construir y registrar eventos.
- `apps/audit/selectors/audit_logs.py`: consultas y acciones ocultas.
- `apps/audit/views/view_audit_log.py`: vista de historial.
- `apps/audit/views/view_export_history.py`: historial, preview y descarga de exportaciones.
- `apps/audit/templates/audit/partials/audit_log/table.html`: tabla visible.
- `apps/audit/templates/audit/partials/export_history/table.html`: tabla de exportaciones.
- `apps/audit/templates/audit/pages/export_preview.html`: preview HTML desde snapshot.
- `apps/audit/services/export_history.py`: registro de snapshot de exportacion.
- `apps/users/services/admin/management.py`: cambios administrativos de usuarios.
- `apps/users/services/auth_service.py`: activacion de cuenta.
- `apps/employees/views/onboarding.py`: registro inicial de ficha.
- `apps/employees/views/view_profile.py`: cambios de perfil y contrasena.
- `apps/vacations/services/requests/review.py`: revision de solicitudes.
- `apps/core/admin.py`: branding general del Django Admin.
- `apps/*/admin.py`: configuracion admin de cada dominio.

Referencia tecnica relacionada:

- [`../docs/conventions/services.md`](../docs/conventions/services.md)
- [`../docs/adr/004-documentation-structure.md`](../docs/adr/004-documentation-structure.md)

## Acciones registradas en auditoria

Estas son las acciones funcionales relevantes en esta version.

### Usuario creado

Accion: `user_created`.

Se registra cuando un admin crea una cuenta desde la gestion de usuarios.

Debe indicar:

- Usuario que creo la cuenta.
- Correo del nuevo usuario.
- DNI normalizado.
- Que la cuenta queda pendiente de activacion.

### Cambio de rol

Accion: `user_primary_role_changed`.

Se registra cuando se reemplaza el rol funcional principal de un usuario.

Importante:

- El sistema no acumula roles desde la interfaz principal.
- Cambiar rol significa sustituir el rol anterior por el nuevo.
- Se protege no dejar el sistema sin administradores funcionales.

Debe indicar:

- Usuario que realizo el cambio.
- Usuario afectado.
- Rol anterior.
- Rol nuevo.

### Cambio de acceso

Accion: `user_access_state_changed`.

Se registra cuando se activa o desactiva manualmente el acceso de un usuario.

Debe indicar:

- Usuario que realizo el cambio.
- Usuario afectado.
- Si el acceso se activo o se desactivo.

Reglas importantes:

- No se puede desactivar el ultimo admin activo.
- No se puede activar una cuenta sin contrasena usable.
- Los superusuarios se gestionan desde Django Admin.

### Datos de usuario

Accion: `user_profile_updated`.

Se registra cuando cambian datos visibles o administrativos del usuario.

Ejemplos:

- Nombre.
- Apellidos.
- Telefono.
- Fecha de ingreso.
- Otros atributos editables de la ficha.

El registro debe listar solo campos con cambios reales.

### Contrasena actualizada

Accion: `user_password_changed`.

Se registra cuando una persona cambia su contrasena desde perfil o cuando una
accion administrativa valida cambia la contrasena de otra persona.

Regla de seguridad:

- Nunca se registra el valor de la contrasena.
- Solo se registra que ocurrio el cambio.

### Cuenta activada

Accion: `user_account_activated`.

Se registra cuando un usuario completa el enlace de activacion y configura su
contrasena inicial.

Debe indicar:

- Usuario activado.
- Que la cuenta quedo configurada con contrasena inicial.

### Solicitud editada

Accion: `vacation_request_reviewed`.

Se registra cuando RRHH o admin modifica una solicitud de vacaciones.

Campos auditados:

- Estado.
- Fecha de inicio.
- Fecha final.
- Dias solicitados.
- Comentario de RRHH anadido, actualizado o eliminado.

El log solo se crea si hubo cambios relevantes.

### Cambio de departamento

Accion: `user_department_changed`.

Esta accion existe a nivel tecnico y se registra si se cambia el departamento
desde servicios administrativos.

Estado de version:

- La logica esta preparada para futuras versiones.
- La interfaz principal oculta la gestion de departamentos.
- El selector de auditoria la mantiene oculta en el historial visible actual.
- Django Admin conserva la gestion completa de departamentos.

## Filtros del historial de actividad

La vista permite revisar eventos con filtros de soporte.

Filtros disponibles:

- Busqueda por usuario o descripcion.
- Tipo de accion.
- Fecha de inicio.
- Fecha final.

Cada fila debe mostrar:

- Fecha y hora.
- Tipo de cambio.
- Usuario que realizo la accion.
- Descripcion de lo ocurrido.
- Enlace de contexto cuando aplica.

Enlaces esperados:

- Eventos de usuario: enlace a gestion/edicion del usuario cuando el rol lo permite.
- Eventos de solicitud: enlace a revision de solicitud cuando el rol lo permite.

## Django Admin

El Django Admin es la herramienta de gestion completa del sistema. Puede exponer
cosas que la interfaz principal no muestra todavia, como departamentos.

Alcance por dominio:

- `users`: usuarios, roles, relacion usuario-rol, activacion y acciones masivas.
- `employees`: fichas de empleado y departamentos.
- `vacations`: estados, solicitudes e historial de solicitud.
- `notifications`: notificaciones internas.
- `audit`: historial de actividad e historial de exportaciones.
- `core`: configuracion visual general del admin.

## Gestion de usuarios desde Django Admin

Debe ser util para soporte interno y administracion tecnica.

Buenas practicas aplicadas:

- Mostrar DNI, email, estado activo y flags administrativos.
- Permitir busqueda por DNI y email.
- Usar filtros por activo, staff, superusuario y roles.
- Editar grupos y permisos cuando sea necesario.
- Ver ficha de empleado relacionada desde inline o campos relacionados.

El Django Admin no sustituye el panel funcional. Es una capa de soporte mas
potente y con mayor responsabilidad.

## Gestion de empleados y departamentos

Aunque departamentos esta oculto en la interfaz principal de esta version, sigue
formando parte del modelo interno.

Django Admin debe permitir:

- Crear departamentos.
- Editar departamentos.
- Asignar empleados a departamentos.
- Revisar fichas de empleados.
- Buscar por nombre, apellidos, usuario o DNI.

Esto deja el sistema preparado para la siguiente version sin bloquear la version
actual de interfaz.

## Gestion de vacaciones desde Django Admin

Django Admin debe permitir:

- Consultar solicitudes.
- Filtrar por estado, fechas y empleado.
- Cambiar estados con acciones controladas.
- Ver historial de solicitud.
- Mantener trazabilidad basica cuando se usan acciones administrativas.

Cuando sea posible, las acciones masivas deben crear registros de historial de
solicitud para no perder contexto.

## Gestion de auditoria y exportaciones

Auditoria e historial de exportaciones son registros sensibles.

Reglas:

- No se editan desde interfaz funcional.
- En Django Admin deben tratarse como lectura o gestion muy restringida.
- No se deben borrar para ocultar cambios de negocio.
- Si se necesita depuracion tecnica, se hace con permisos administrativos claros.

### Historial de exportaciones

El historial de exportaciones no guarda archivos Excel en disco. Guarda
metadatos y un snapshot JSON de las filas exportadas.

Campos relevantes:

- `file_name`: nombre visible de descarga.
- `filters_json`: filtros usados en el listado.
- `rows_snapshot_json`: filas exactas que se exportaron.
- `columns_version`: version de estructura de columnas.
- `total_records`: cantidad de solicitudes exportadas.
- `status`: `pending`, `success` o `failed`.

Desde la interfaz funcional:

- La exportacion inicial genera snapshot y descarga el Excel en memoria.
- La preview historica renderiza una tabla HTML desde `rows_snapshot_json`.
- La descarga historica regenera el `.xlsx` desde `rows_snapshot_json`.
- Ni preview ni descarga historica crean nuevas exportaciones.

## Checklist antes de anadir una accion auditada

Antes de crear una nueva accion:

- Confirmar que es un evento importante para negocio o seguridad.
- Definir un nombre interno estable.
- Definir una etiqueta visible en espanol.
- Registrar actor, recurso y descripcion.
- Evitar guardar datos sensibles.
- Cubrir el evento con tests.
- Documentarlo en esta guia.

## Tests recomendados

Cuando se toca auditoria o admin, revisar o ampliar tests en:

- `apps/audit/tests/test_audit_log_view.py`
- `apps/audit/tests/test_export_history_view.py`
- `apps/users/tests/test_admin_users.py`
- `apps/vacations/tests/test_review_request_view.py`

Casos minimos a cubrir:

- Crear usuario registra auditoria.
- Cambiar rol registra rol anterior y nuevo.
- Cambiar acceso registra activacion o desactivacion.
- Activar cuenta desde enlace registra auditoria.
- Cambiar perfil o contrasena registra auditoria sin valores sensibles.
- Revisar solicitud registra cambios de estado, fechas, dias o comentario.
- Acciones ocultas como departamento no aparecen en la interfaz principal.
- Exportar Excel registra snapshot y permite preview/descarga historica.
