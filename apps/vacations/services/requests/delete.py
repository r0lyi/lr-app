"""Eliminacion controlada de solicitudes de vacaciones."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .policies import OPEN_REQUEST_STATUS_NAMES


def delete_pending_vacation_request(vacation_request):
    """Elimina una solicitud solo si todavia esta pendiente de revision."""

    status_name = (vacation_request.status.name or "").strip().lower()
    if status_name not in OPEN_REQUEST_STATUS_NAMES:
        raise ValidationError(
            _("Solo puedes eliminar solicitudes que sigan en estado pendiente."),
        )

    vacation_request.delete()
