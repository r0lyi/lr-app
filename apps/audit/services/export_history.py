"""Servicios para registrar y completar exportaciones realizadas por usuarios.

Este modulo concentra la logica de persistencia del historial de exportaciones
para que las vistas y los dominios de negocio no tengan que conocer detalles
de almacenamiento en disco ni del modelo `ExportHistory`.
"""

from pathlib import Path

from django.conf import settings

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


def get_exports_root():
    """Devuelve la carpeta raiz donde se guardan los archivos exportados."""

    exports_root = Path(settings.EXPORTS_ROOT)
    exports_root.mkdir(parents=True, exist_ok=True)
    return exports_root


def mark_export_success(*, export_history, file_name, file_bytes, total_records):
    """Guarda el archivo generado y marca el historial como exitoso."""

    export_dir = get_exports_root() / (export_history.export_type or "general")
    export_dir.mkdir(parents=True, exist_ok=True)

    export_path = export_dir / file_name
    export_path.write_bytes(file_bytes)

    export_history.file_name = file_name
    export_history.file_path = str(export_path)
    export_history.total_records = total_records
    export_history.status = EXPORT_STATUS_SUCCESS
    export_history.save(
        update_fields=[
            "file_name",
            "file_path",
            "total_records",
            "status",
        ]
    )

    return export_path


def mark_export_failed(*, export_history):
    """Marca la exportacion como fallida cuando no se pudo generar."""

    export_history.status = EXPORT_STATUS_FAILED
    export_history.save(update_fields=["status"])
