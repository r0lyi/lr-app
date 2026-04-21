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
El resultado se descarga directamente en el navegador como archivo `.xlsx`; no
se envia por correo electronico.

Columnas del archivo, en orden:

- Numero empleado.
- Apellidos.
- Nombre.
- Fecha inicio.
- Fecha final.
- Telefono.
- Dias solicitados.

El archivo define anchos de columna legibles y cabecera en negrita para evitar
que los textos queden ocultos al abrirlo.

Cada exportacion guarda un snapshot JSON de las filas exportadas en
`ExportHistory.rows_snapshot_json`. El historial no depende de archivos en disco:
al descargar o previsualizar una exportacion historica, el Excel o la tabla se
regeneran desde ese snapshot.

Los nombres de archivo usan fecha ISO y sufijo corto unico:

`vacation_2026-04-21_9f3a2c.xlsx`

### Flujo completo desde el boton de exportar

1. El usuario pulsa `Exportar Excel` desde el panel de solicitudes de RRHH o
   admin.
2. El enlace conserva los filtros actuales del listado, excepto la paginacion.
   Si no llega filtro de estado, se usa `pending` como valor por defecto.
3. La vista `export_rrhh_requests_excel_view` valida los filtros con
   `RrhhVacationRequestFilterForm`.
4. Con filtros validos, la vista consulta las solicitudes con
   `get_filtered_rrhh_vacation_requests`.
5. El servicio `build_rrhh_export_review` aplica la revision previa: orden de
   antiguedad, alertas internas y listado final que se exporta.
6. Antes de generar el archivo, se crea un `ExportHistory` en estado `pending`
   con usuario, tipo de exportacion y filtros serializados.
7. El servicio `build_rrhh_vacation_requests_excel` construye tres piezas desde
   el mismo listado revisado:
   - `file_name`, con formato `vacation_YYYY-MM-DD_xxxxxx.xlsx`.
   - `file_bytes`, el `.xlsx` generado en memoria.
   - `snapshot_rows`, una lista JSON-safe con las filas exactas exportadas.
8. Si la generacion termina correctamente, `mark_export_success` actualiza el
   historial a `success` y guarda:
   - `file_name`.
   - `rows_snapshot_json`.
   - `columns_version`.
   - `total_records`.
9. La vista devuelve `file_bytes` como `HttpResponse` con
   `Content-Disposition: attachment`, por lo que el navegador descarga el Excel
   directamente en el ordenador del usuario.
10. Si algo falla durante la generacion, `mark_export_failed` marca el historial
    como `failed` y el usuario vuelve al panel con un mensaje de error.

No se guarda ningun archivo `.xlsx` en carpetas locales. El archivo solo existe
como bytes durante la respuesta de descarga; la evidencia persistente es el
snapshot guardado en base de datos.

Debe registrar:

- Usuario que exporto.
- Tipo de exportacion.
- Nombre de archivo.
- Snapshot JSON.
- Version de columnas.
- Fecha de creacion.
- Total de registros si el servicio lo informa.

## Historial de exportaciones

La vista de historial muestra exportaciones reales realizadas por usuarios.

Cada fila del historial usa los metadatos guardados en `ExportHistory`:

- Fecha de creacion.
- Usuario que genero la exportacion.
- Nombre del archivo.
- Total de solicitudes exportadas.
- Acciones disponibles.

Desde el historial hay dos acciones sobre una exportacion:

- `Vista previa`: renderiza una tabla HTML desde `rows_snapshot_json`; no genera
  ni guarda un archivo temporal.
- `Descargar`: regenera el `.xlsx` en memoria desde `rows_snapshot_json` y lo
  entrega como descarga directa.

Reglas actuales:

- Solo cuenta exportaciones de solicitudes de vacaciones de RRHH.
- No cuenta descargas posteriores del historial.
- No cuenta vistas previas del historial.
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
- Guarda snapshot JSON con las filas exportadas.
- Regenera la descarga historica desde snapshot.
- Muestra preview historica desde snapshot.
- No registra una nueva exportacion al descargar desde el historial.
