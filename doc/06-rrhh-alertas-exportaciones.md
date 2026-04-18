# RRHH: alertas, revision previa y exportaciones

Esta guia explica el panel de gestion de solicitudes de RRHH, las alertas antes
de exportar y el historial de exportaciones.

## Objetivo del flujo

RRHH necesita ver solicitudes, filtrarlas, detectar riesgos y exportar datos sin
tener que revisar manualmente cada posible conflicto.

El sistema ayuda con:

- Alertas visibles antes de exportar.
- Registro desplegable de detalles.
- Orden interno por antiguedad.
- Historial de exportaciones realizadas.
- Preparacion para reglas futuras como periodos de alta carga.

## Archivos principales

- `apps/vacations/views/rrhh/requests_management.py`: vista del listado de RRHH.
- `apps/vacations/views/rrhh/export_requests_excel.py`: exportacion a Excel.
- `apps/vacations/services/export/review.py`: revision previa y alertas.
- `apps/vacations/services/export/excel.py`: generacion del archivo.
- `apps/vacations/services/requests/policies.py`: constantes compartidas.
- `apps/audit/services/export_history.py`: registro de exportaciones.
- `apps/audit/views/view_export_history.py`: vista del historial.
- `apps/audit/selectors/export_history.py`: consulta del historial.
- `apps/vacations/templates/vacations/partials/requests_management/export_review_summary.html`: panel de alertas.

Referencia tecnica relacionada:

- [`../docs/conventions/services.md`](../docs/conventions/services.md)
- [`../docs/conventions/templates.md`](../docs/conventions/templates.md)

## Revision previa de RRHH

La funcion `build_rrhh_export_review` recibe solicitudes ya filtradas y devuelve:

- Solicitudes ordenadas para revision.
- Contadores de advertencias.
- Alertas internas completas.
- Alertas visibles para la interfaz.

La vista usa esta informacion para mostrar un bloque de alerta profesional antes
de exportar. Ese bloque no bloquea la exportacion por si solo; su funcion es
ayudar a RRHH a tomar una decision informada.

## Orden interno por antiguedad

Las solicitudes se ordenan internamente con:

- Fecha de ingreso del empleado.
- Fecha de inicio de la solicitud.
- Fecha de registro de la solicitud.
- Identificador de solicitud.

Este orden da prioridad natural a empleados con mas tiempo en la empresa cuando
hay que revisar listados complejos.

Importante:

- El sistema mantiene esta regla internamente.
- No se muestra como alerta visible en esta version.
- La entrada `seniority` puede existir en el resumen interno, pero no aparece en
  el registro desplegable visible.

## Alertas visibles

Actualmente el registro desplegable muestra dos tipos de alerta.

### Solapamientos de fechas

Tipo interno: `overlap`.

Se detecta cuando una solicitud coincide en fechas con solicitudes activas de
otros empleados del mismo departamento.

Detalles mostrados:

- Empleado de la solicitud revisada.
- Rango solicitado.
- Dias solicitados.
- Empleados con los que coincide.
- Rangos de vacaciones que producen el solapamiento.
- Estado de las solicitudes que causan la coincidencia.

Estados considerados activos:

- `pending`
- `approved`

Nota de version:

- Aunque la interfaz principal ya no expone gestion de departamentos, la logica
  esta preparada a nivel de datos para futuras versiones.
- Si un empleado no tiene departamento, no se calculan solapamientos por
  departamento.

### Solicitud de larga duracion

Tipo interno: `long_duration`.

Se detecta cuando la solicitud tiene exactamente 30 dias naturales, segun
`LONG_DURATION_VACATION_DAYS`.

Detalles mostrados:

- Empleado.
- Fecha de inicio.
- Fecha final.
- Total de dias solicitados.

Esta alerta no significa que la solicitud sea incorrecta. Solo indica que RRHH
debe revisarla con mas cuidado porque consume el maximo permitido en una sola
peticion.

## Log desplegable de alertas

El panel visible funciona como un registro plegable:

- Cerrado, muestra contadores y resumen.
- Abierto, muestra las entradas detalladas.
- El estilo visual usa una advertencia amarilla para indicar revision necesaria
  sin transmitir error critico.

Regla de producto:

- El registro visible debe mostrar informacion accionable.
- No debe mostrar reglas internas que no aportan decision directa al usuario.

Por eso no se muestra el orden por antiguedad como alerta visible.

## Alta carga preparada para futuras versiones

El servicio ya calcula coincidencias con periodos de alta carga usando
`HIGH_LOAD_PERIODS`.

Periodos preparados actualmente:

- Verano.
- Navidad.

Estado actual:

- La logica existe.
- El contador interno puede calcularse.
- No se muestra en el registro visible de esta version.

Cuando se active en interfaz, conviene documentar:

- Criterio exacto por calendario laboral.
- Si bloquea, advierte o solo etiqueta.
- Si afecta a todos los departamentos o solo a equipos concretos.

## Exportacion a Excel

La exportacion se ejecuta desde la vista de RRHH con los filtros actuales.

Debe registrar:

- Usuario que exporto.
- Tipo de exportacion.
- Nombre de archivo.
- Ruta de archivo.
- Fecha de creacion.
- Total de registros si el servicio lo informa.

El archivo se guarda en `var/exports/`, fuera del codigo versionado.

## Historial de exportaciones

La vista de historial muestra exportaciones reales realizadas por usuarios.

Reglas actuales:

- Solo cuenta exportaciones de solicitudes de vacaciones de RRHH.
- No cuenta descargas posteriores del historial.
- Muestra contador de total de exportaciones.
- Muestra fecha de la ultima exportacion.
- Permite filtrar por fecha.
- Usa paginacion compartida del dashboard.

Esto evita inflar metricas: descargar un archivo ya exportado no es una nueva
exportacion de negocio.

## Tests recomendados

Cuando se toca este flujo, revisar o ampliar tests en:

- `apps/vacations/tests/test_export_review_service.py`
- `apps/vacations/tests/test_export_rrhh_requests_excel.py`
- `apps/audit/tests/test_export_history_view.py`

Casos minimos a cubrir:

- Detecta solapamientos por departamento.
- Ignora solicitudes rechazadas en solapamientos.
- No falla si el empleado no tiene departamento.
- Detecta solicitudes de 30 dias.
- Mantiene alta carga calculada aunque no sea visible.
- Registra exportaciones reales.
- No registra una nueva exportacion al descargar desde el historial.
