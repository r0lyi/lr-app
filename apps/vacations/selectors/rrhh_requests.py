"""Consultas de lectura para el panel basico de RRHH."""

from django.db.models import Q

from apps.vacations.models import VacationRequest


def get_rrhh_vacation_requests():
    """Devuelve las solicitudes visibles para RRHH en esta primera fase.

    Por ahora RRHH solo necesita una tabla basica con los datos esenciales de
    cada solicitud. Dejamos la consulta en el dominio `vacations` para que el
    dashboard no cargue con logica de negocio ajena.
    """

    return (
        VacationRequest.objects.select_related("employee", "employee__user", "status")
        .order_by("-request_date", "-id")
    )


def get_filtered_rrhh_vacation_requests(
    *,
    search="",
    start_date=None,
    end_date=None,
    status_name="",
):
    """Aplica filtros sobre la tabla base visible para RRHH.

    `search` busca por nombre o apellido del empleado asociado.
    `start_date` y `end_date` recortan el rango solicitado mostrado.
    `status_name` permite ver solo un estado concreto.
    """

    requests_qs = get_rrhh_vacation_requests()

    normalized_search = (search or "").strip()
    if normalized_search:
        requests_qs = requests_qs.filter(
            Q(employee__first_name__icontains=normalized_search)
            | Q(employee__last_name__icontains=normalized_search)
        )

    if start_date is not None:
        requests_qs = requests_qs.filter(start_date__gte=start_date)

    if end_date is not None:
        requests_qs = requests_qs.filter(end_date__lte=end_date)

    normalized_status_name = (status_name or "").strip().lower()
    if normalized_status_name:
        requests_qs = requests_qs.filter(status__name=normalized_status_name)

    return requests_qs
