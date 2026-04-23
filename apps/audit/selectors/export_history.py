"""Consultas de lectura para el historial de exportaciones."""

from apps.audit.models import ExportHistory


def get_export_histories(*, export_type=None, start_date=None, end_date=None):
    """Devuelve el historial ordenado por fecha descendente.

    `export_type` permite limitar la lista a un tipo concreto de exportacion,
    por ejemplo las exportaciones del panel de RRHH.
    `start_date` y `end_date` filtran por la fecha de creacion del registro.
    """

    histories = ExportHistory.objects.select_related("user").order_by("-created_at")

    if export_type:
        histories = histories.filter(export_type=export_type)

    if start_date is not None:
        histories = histories.filter(created_at__date__gte=start_date)

    if end_date is not None:
        histories = histories.filter(created_at__date__lte=end_date)

    return histories


def get_export_history_by_id(export_history_id):
    """Obtiene un registro concreto con su usuario asociado."""

    return ExportHistory.objects.select_related("user").get(pk=export_history_id)
