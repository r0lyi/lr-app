# Services y Selectors

Esta convencion define donde vive la logica de negocio. El objetivo es que una
vista sea facil de leer y que las reglas importantes no se dupliquen entre
formularios, templates o JavaScript.

## Regla principal

- `views`: HTTP, permisos, formularios, mensajes y redirecciones.
- `services`: casos de uso, validaciones de escritura y efectos secundarios.
- `selectors`: consultas ORM de lectura reutilizables.
- `forms`: validacion de formato de entrada, no reglas profundas de negocio.
- `utils`: helpers genericos sin conocimiento fuerte del dominio.

## Views

Una vista debe responder a estas preguntas:

- Quien puede entrar.
- Que formulario se usa.
- Que servicio se llama.
- A donde se redirige.
- Que contexto visual necesita el template.

Una vista no debe:

- Repetir validaciones de negocio.
- Calcular saldos o reglas sensibles si ya existe un servicio.
- Crear logs de auditoria directamente salvo que el caso de uso sea puramente de vista.
- Construir queries complejas que se reutilizan en otros sitios.

Ejemplo correcto:

```text
view -> form.is_valid() -> service(...) -> messages -> redirect/render
```

## Services

Los servicios ejecutan acciones de negocio.

Responsabilidades:

- Validar reglas antes de escribir.
- Crear, actualizar o eliminar modelos.
- Mantener transacciones cuando una accion toca varias tablas.
- Disparar efectos secundarios del caso de uso.
- Traducir errores de negocio a `ValidationError` cuando aplica.

Ejemplos del proyecto:

- `create_employee_vacation_request`: crea una solicitud pendiente y notifica a RRHH.
- `delete_pending_vacation_request`: elimina solo solicitudes pendientes.
- `review_vacation_request`: revisa solicitud, recalcula dias, notifica y audita.
- `create_admin_user`: crea usuario con DNI/email, genera activacion y audita.
- `change_user_primary_role`: reemplaza rol funcional y audita el cambio.

## Validaciones de escritura

Toda validacion que protege datos debe vivir en `services` o en validadores
llamados por servicios.

Checklist antes de guardar:

- Validar permisos de negocio que no dependan solo del decorador.
- Validar estado actual del recurso.
- Validar rangos de fechas.
- Validar duplicados o solapamientos.
- Validar saldos, cuotas o limites.
- Validar que el cambio no rompe una regla de seguridad.
- Validar que el dato normalizado coincide con el formato esperado.

Ejemplos:

- DNI normalizado y con letra en mayuscula antes de comparar.
- Solicitud de vacaciones con fecha de inicio futura.
- Solicitud con minimo 30 dias de antelacion.
- Solicitud entre 3 y 30 dias naturales.
- Eliminacion permitida solo en estado `pending`.
- No desactivar el ultimo admin activo.
- No activar una cuenta sin contrasena usable.

## Selectors

Los selectors concentran lecturas reutilizables.

Responsabilidades:

- Encapsular queries ORM compartidas.
- Aplicar `select_related` y `prefetch_related` cuando mejora rendimiento.
- Devolver QuerySets cuando la vista necesita filtrar o paginar.
- Devolver objetos concretos cuando el nombre lo indique claramente.

Ejemplos:

- `get_overlapping_active_requests`.
- `get_reserved_annual_vacation_days_for_year`.
- `get_export_histories`.
- `get_audit_logs`.

Un selector no debe:

- Crear registros.
- Enviar notificaciones.
- Registrar auditoria.
- Cambiar estados.

## Auditoria y efectos secundarios

Los efectos secundarios deben ocurrir desde el servicio o desde la vista de caso
de uso si no hay servicio dedicado.

Efectos secundarios habituales:

- Notificaciones internas.
- Logs de actividad.
- Historial de exportaciones.
- Historial de solicitud.
- Envio de email de activacion.

Regla practica:

- Si una accion cambia datos de negocio, el servicio debe decidir si audita.
- Si una accion solo descarga o renderiza, normalmente no debe auditar.
- Si una descarga representa una exportacion nueva, debe registrar historial.
- Si una descarga recupera un archivo ya exportado, no debe crear nueva exportacion.

Acciones auditadas actualmente:

- `user_created`
- `user_primary_role_changed`
- `user_access_state_changed`
- `user_profile_updated`
- `user_password_changed`
- `user_account_activated`
- `vacation_request_reviewed`

Accion preparada pero oculta en UI principal:

- `user_department_changed`

## Transacciones

Usa `transaction.atomic()` cuando una accion necesita que varias escrituras sean
coherentes.

Ejemplos:

- Crear usuario, generar activacion y registrar auditoria.
- Revisar solicitud y crear historial/notificacion si se anade en el mismo caso.
- Acciones admin que actualizan varios modelos relacionados.

Si una parte falla, el sistema debe quedar en un estado comprensible.

## Imports entre apps

Para evitar dependencias circulares:

- Importa modelos y selectors arriba cuando no crean ciclos.
- Importa servicios de auditoria dentro de la funcion si generan ciclos.
- Evita que `audit` dependa de detalles internos innecesarios de cada dominio.

Ejemplo aceptado:

```python
def change_user_primary_role(...):
    ...
    from apps.audit.services import log_user_primary_role_changed
    log_user_primary_role_changed(...)
```

## Tests esperados

Cada servicio con reglas de negocio debe tener tests de:

- Caso correcto.
- Error por validacion.
- Error por estado no permitido.
- Efectos secundarios esperados.
- Ausencia de efectos secundarios cuando no hay cambios reales.

No basta con testear la vista si la regla vive en el servicio.
