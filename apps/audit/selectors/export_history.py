"""Consultas de lectura para el historial de exportaciones."""

from apps.audit.models import ExportHistory


def get_export_histories(*, export_type=None):
    """Devuelve el historial ordenado por fecha descendente.

    `export_type` permite limitar la lista a un tipo concreto de exportacion,
    por ejemplo las exportaciones del panel de RRHH.
    """

    histories = ExportHistory.objects.select_related("user").order_by("-created_at")

    if export_type:
        histories = histories.filter(export_type=export_type)

    return histories


def get_export_history_by_id(export_history_id):
    """Obtiene un registro concreto con su usuario asociado."""

    return ExportHistory.objects.select_related("user").get(pk=export_history_id)

