"""Reglas basicas para la revision de solicitudes por parte de RRHH."""

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.notifications.services import (
    create_vacation_status_changed_notification,
)
from apps.users.selectors import has_role
from apps.vacations.selectors import get_overlapping_active_requests

from .policies import ACTIVE_REQUEST_STATUS_NAMES
from .validators import calculate_requested_natural_days


def review_vacation_request(
    vacation_request,
    *,
    acting_user,
    status,
    start_date,
    end_date,
    hr_comment="",
):
    """Actualiza estado y fechas de una solicitud existente.

    Reglas basicas que aplicamos en esta fase:
    - la fecha final no puede ser anterior al inicio
    - si la solicitud queda activa (pending/approved), no puede solaparse con
      otra solicitud activa del mismo empleado
    - requested_days se recalcula al cambiar el rango
    - resolution_date solo se fija cuando la solicitud deja de estar pendiente
    - resolved_by guarda quien hizo la ultima resolucion desde RRHH
    - un usuario RRHH no puede revisar una solicitud propia
    - solo notificamos al empleado cuando el estado cambia realmente
    """
    previous_status_name = vacation_request.status.name
    previous_start_date = vacation_request.start_date
    previous_end_date = vacation_request.end_date
    previous_requested_days = vacation_request.requested_days
    previous_hr_comment = vacation_request.hr_comment

    if (
        vacation_request.employee.user_id == acting_user.id
        and has_role(acting_user, "rrhh")
    ):
        raise ValidationError(
            "No puedes revisar tu propia solicitud de vacaciones. Debe gestionarla otro usuario de RRHH."
        )

    if end_date < start_date:
        raise ValidationError(
            "La fecha final no puede ser anterior a la fecha de inicio."
        )

    if status.name in ACTIVE_REQUEST_STATUS_NAMES:
        overlapping_requests = get_overlapping_active_requests(
            vacation_request.employee,
            start_date=start_date,
            end_date=end_date,
            exclude_request_id=vacation_request.pk,
        )
        if overlapping_requests.exists():
            raise ValidationError(
                "Ya existe otra solicitud activa del empleado que se solapa con ese periodo."
            )

    new_requested_days = calculate_requested_natural_days(
        start_date,
        end_date,
    )

    vacation_request.status = status
    vacation_request.start_date = start_date
    vacation_request.end_date = end_date
    vacation_request.requested_days = new_requested_days
    vacation_request.hr_comment = hr_comment.strip() or None
    vacation_request.resolution_date = (
        timezone.now() if status.name != "pending" else None
    )
    vacation_request.resolved_by = acting_user if status.name != "pending" else None
    vacation_request.save(
        update_fields=[
            "status",
            "start_date",
            "end_date",
            "requested_days",
            "hr_comment",
            "resolution_date",
            "resolved_by",
            "updated_at",
        ]
    )

    create_vacation_status_changed_notification(
        vacation_request,
        previous_status_name=previous_status_name,
        new_status_name=status.name,
    )

    from apps.audit.services import log_vacation_request_reviewed

    log_vacation_request_reviewed(
        acting_user=acting_user,
        vacation_request=vacation_request,
        previous_status_name=previous_status_name,
        new_status_name=status.name,
        previous_start_date=previous_start_date,
        new_start_date=start_date,
        previous_end_date=previous_end_date,
        new_end_date=end_date,
        previous_requested_days=previous_requested_days,
        new_requested_days=new_requested_days,
        previous_hr_comment=previous_hr_comment,
        new_hr_comment=vacation_request.hr_comment,
    )

    return vacation_request
