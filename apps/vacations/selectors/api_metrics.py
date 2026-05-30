"""Consultas agregadas para endpoints API de vacaciones."""

from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count

from apps.vacations.models import VacationRequest


def _percentage(part, total):
    """Calcula porcentajes con dos decimales para respuestas KPI."""

    if not total:
        return 0.0
    value = Decimal(part) / Decimal(total) * Decimal("100")
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def get_vacation_request_kpis():
    """Devuelve metricas generales de solicitudes de vacaciones."""

    requests = VacationRequest.objects.select_related(
        "employee__department",
        "status",
    )
    total_requests = requests.count()
    pending_requests = requests.filter(status__name="pending").count()
    approved_requests = requests.filter(status__name="approved").count()
    rejected_requests = requests.filter(status__name="rejected").count()

    departments = (
        requests.filter(employee__department__isnull=False)
        .values(
            "employee__department_id",
            "employee__department__name",
        )
        .annotate(total_solicitudes=Count("id"))
        .order_by("-total_solicitudes", "employee__department__name")
    )

    return {
        "total_solicitudes": total_requests,
        "solicitudes_pendientes": pending_requests,
        "solicitudes_aprobadas": approved_requests,
        "solicitudes_rechazadas": rejected_requests,
        "porcentaje_aprobacion": _percentage(approved_requests, total_requests),
        "porcentaje_rechazo": _percentage(rejected_requests, total_requests),
        "departamentos_con_mas_solicitudes": [
            {
                "id": row["employee__department_id"],
                "nombre": row["employee__department__name"],
                "total_solicitudes": row["total_solicitudes"],
            }
            for row in departments
        ],
    }
