"""Servicios para registrar exportaciones realizadas por usuarios."""

from apps.audit.models import ExportHistory

EXPORT_TYPE_RRHH_VACATION_REQUESTS = "rrhh_vacation_requests"

EXPORT_STATUS_PENDING = "pending"
EXPORT_STATUS_SUCCESS = "success"
EXPORT_STATUS_FAILED = "failed"


def serialize_export_filters(filters):
    """Convierte filtros arbitrarios a un diccionario JSON-safe.

    Las fechas del formulario llegan como instancias `date` y no son
    serializables directamente por `JSONField`. Por eso normalizamos cada
    valor antes de guardarlo en el historial.
    """

    serialized_filters = {}

    for key, value in (filters or {}).items():
        if hasattr(value, "isoformat"):
            serialized_filters[key] = value.isoformat()
        else:
            serialized_filters[key] = value

    return serialized_filters


def create_export_history(*, user, export_type, filters):
    """Crea un registro inicial en estado `pending`.

    Este paso se hace antes de generar el archivo para dejar trazabilidad
    incluso si la exportacion falla mas tarde.
    """

    return ExportHistory.objects.create(
        user=user,
        export_type=export_type,
        status=EXPORT_STATUS_PENDING,
        filters_json=serialize_export_filters(filters),
    )


def mark_export_success(
    *,
    export_history,
    file_name,
    rows_snapshot,
    columns_version,
    total_records,
):
    """Guarda el snapshot exportado y marca el historial como exitoso."""

    export_history.file_name = file_name
    export_history.rows_snapshot_json = rows_snapshot
    export_history.columns_version = columns_version
    export_history.total_records = total_records
    export_history.status = EXPORT_STATUS_SUCCESS
    export_history.save(
        update_fields=[
            "file_name",
            "rows_snapshot_json",
            "columns_version",
            "total_records",
            "status",
        ]
    )


def mark_export_failed(*, export_history):
    """Marca la exportacion como fallida cuando no se pudo generar."""

    export_history.status = EXPORT_STATUS_FAILED
    export_history.save(update_fields=["status"])
