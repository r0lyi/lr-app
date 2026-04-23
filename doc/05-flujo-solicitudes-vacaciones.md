# Flujo de solicitudes de vacaciones

Esta guia explica que ocurre cuando una persona solicita vacaciones, que se
valida antes de guardar, que efectos secundarios se generan y donde vive cada
pieza de logica.

## Objetivo del flujo

El sistema permite que cualquier usuario con ficha de empleado cree una
solicitud de vacaciones. La solicitud nace en estado `pending` y queda lista
para que RRHH o administracion la revise.

El flujo esta pensado para proteger tres cosas:

- Que la persona no pida fechas invalidas.
- Que no se consuman mas dias de los disponibles.
- Que RRHH pueda revisar el impacto antes de aprobar o exportar.

## Archivos principales

- `apps/vacations/forms/request_vacation.py`: formulario HTTP de fechas y comentario.
- `apps/vacations/forms/employee_request_filters.py`: filtros del historial del empleado.
- `apps/vacations/forms/rrhh_request_filters.py`: filtros del listado RRHH/admin.
- `apps/vacations/forms/review_request.py`: formulario de revision RRHH/admin.
- `apps/vacations/views/employee/create_request.py`: vista de alta de solicitud.
- `apps/vacations/views/employee/delete_request.py`: vista de eliminacion.
- `apps/vacations/views/rrhh/requests_management.py`: listado compartido RRHH/admin.
- `apps/vacations/views/rrhh/review_request.py`: vista de revision.
- `apps/vacations/services/requests/create.py`: caso de uso para crear.
- `apps/vacations/services/requests/delete.py`: caso de uso para eliminar.
- `apps/vacations/services/requests/review.py`: caso de uso para revisar desde RRHH/admin.
- `apps/vacations/services/requests/validators.py`: validaciones de negocio.
- `apps/vacations/services/requests/policies.py`: constantes de negocio.
- `apps/vacations/selectors/request_queries.py`: consultas reutilizables.

Referencia tecnica relacionada:

- [`../docs/conventions/services.md`](../docs/conventions/services.md)
- [`../docs/architecture/project_structure.md`](../docs/architecture/project_structure.md)

## Paso 1: entrada por vista

La vista `create_vacation_request_view` hace solo orquestacion:

- Comprueba que el usuario tenga ficha de empleado.
- Si no tiene ficha, lo redirige al onboarding.
- Construye el formulario.
- Llama al servicio `create_employee_vacation_request`.
- Prepara contexto visual como saldo anual, fecha minima y resumen.

La vista no debe duplicar reglas como "minimo 30 dias de antelacion" o
"maximo 30 dias solicitados". Esas reglas viven en servicios y policies.

## Paso 2: validaciones antes de registrar

Antes de crear una solicitud se ejecuta `validate_employee_vacation_request`.

Checklist de validaciones:

- La fecha final no puede ser anterior a la fecha de inicio.
- El modo de conteo configurado debe ser `natural`.
- La fecha de inicio no puede estar en el pasado.
- La fecha de inicio debe cumplir al menos 30 dias naturales de antelacion.
- La solicitud debe tener entre 3 y 30 dias naturales.
- Los dias solicitados no pueden superar el saldo anual disponible.
- No puede existir otra solicitud activa del mismo empleado que se solape.

Estados considerados activos para saldo y solapamiento:

- `pending`
- `approved`

Esto significa que una solicitud pendiente ya reserva dias. Asi evitamos que un
empleado envie varias solicitudes pendientes que juntas superen su derecho anual.

## Paso 3: calculo de dias

El proyecto trabaja actualmente con dias naturales.

Ejemplo:

```text
Inicio: 10/08/2026
Fin:    14/08/2026
Total:  5 dias naturales
```

El calculo vive en `calculate_requested_natural_days` y es inclusivo:

- Cuenta el dia de inicio.
- Cuenta el dia de fin.
- Devuelve un decimal normalizado para trabajar de forma consistente con el modelo.

## Paso 4: saldo anual

El saldo anual se calcula desde `get_request_annual_balance`.

Formula conceptual:

```text
saldo disponible = derecho anual - dias reservados en solicitudes activas
```

El derecho anual base esta centralizado en `FULL_ANNUAL_VACATION_DAYS`.
Actualmente el valor completo es 30 dias, con calculo proporcional cuando aplica
segun la fecha de ingreso del empleado.

Los dias reservados se obtienen con
`get_reserved_annual_vacation_days_for_year`, que suma solicitudes `pending` y
`approved` del empleado en el ano de referencia.

## Paso 5: creacion de la solicitud

Cuando todas las validaciones pasan, `create_employee_vacation_request` crea la
solicitud con:

- Empleado propietario.
- Fecha de inicio.
- Fecha final.
- Dias solicitados calculados.
- Estado inicial `pending`.
- Comentario del empleado limpio, o vacio si no se escribio nada.

Despues se avisa a RRHH mediante notificaciones internas para que la solicitud
no quede invisible.

## Paso 6: eliminacion por el empleado

El empleado puede eliminar una solicitud solo si sigue pendiente.

Reglas:

- La accion debe venir desde la vista propietaria del empleado.
- La solicitud debe pertenecer al empleado autenticado.
- El estado debe estar dentro de `OPEN_REQUEST_STATUS_NAMES`.
- Actualmente `OPEN_REQUEST_STATUS_NAMES` contiene solo `pending`.

Si la solicitud ya fue aprobada o rechazada, no se elimina desde el panel de
empleado. En ese caso la correccion debe pasar por RRHH o administracion.

## Paso 7: revision por RRHH o administracion

La revision usa `review_vacation_request`.

Durante una revision se puede cambiar:

- Estado.
- Fecha de inicio.
- Fecha final.
- Comentario de RRHH.

Antes de guardar se validan reglas importantes:

- RRHH no puede revisar su propia solicitud.
- La fecha final no puede ser anterior a la fecha de inicio.
- El nuevo rango no puede solaparse con otra solicitud activa del mismo empleado.
- Los dias solicitados se recalculan si cambia el rango.

Efectos secundarios:

- Se guarda `resolved_by` cuando corresponde.
- Se guarda `resolution_date` cuando corresponde.
- Se notifica al empleado si cambia el estado.
- Se registra auditoria si hubo cambios relevantes.

## Auditoria relacionada

Una revision de solicitud genera accion `vacation_request_reviewed` cuando
cambia algun dato relevante.

Campos auditados:

- Estado anterior y nuevo.
- Fecha de inicio anterior y nueva.
- Fecha final anterior y nueva.
- Dias solicitados anteriores y nuevos.
- Comentario de RRHH anadido, actualizado o eliminado.

Mas detalle en [`07-auditoria-y-admin-django.md`](./07-auditoria-y-admin-django.md).

## Tests recomendados

Cuando se toca este flujo, revisar o ampliar tests en:

- `apps/vacations/tests/test_request_vacation_view.py`
- `apps/vacations/tests/test_review_request_view.py`
- `apps/dashboard/tests/test_dashboard_routing.py`

Casos minimos a cubrir:

- No permite fechas en pasado.
- No permite menos de 30 dias de antelacion.
- No permite menos de 3 ni mas de 30 dias.
- No permite superar saldo anual.
- No permite solapamientos del mismo empleado.
- Permite eliminar solo si esta pendiente.
- La revision recalcula dias y registra auditoria.
