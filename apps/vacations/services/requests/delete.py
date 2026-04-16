"""Eliminacion controlada de solicitudes de vacaciones."""

from django.core.exceptions import ValidationError

from .policies import OPEN_REQUEST_STATUS_NAMES


def delete_pending_vacation_request(vacation_request):
    """Elimina una solicitud solo si todavia esta pendiente de revision."""

    status_name = (vacation_request.status.name or "").strip().lower()
    if status_name not in OPEN_REQUEST_STATUS_NAMES:
        raise ValidationError(
            "Solo puedes eliminar solicitudes que sigan en estado pendiente.",
        )

    vacation_request.delete()
