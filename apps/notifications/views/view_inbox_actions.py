"""Vistas pequenas para interactuar con el inbox interno."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from apps.notifications.selectors import get_user_inbox_notification_by_id
from apps.notifications.services import (
    mark_all_notifications_as_read,
    mark_notification_as_read,
)


def _get_notifications_redirect_target(request):
    """Calcula a donde volver tras una accion rapida del panel."""

    redirect_to = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect_to or "/"


@require_POST
@login_required(login_url="/auth/login/")
def mark_notification_as_read_view(request, notification_id):
    """Marca una notificacion concreta como leida y vuelve a la pagina actual."""

    notification = get_user_inbox_notification_by_id(request.user, notification_id)
    mark_notification_as_read(notification)
    return redirect(_get_notifications_redirect_target(request))


@require_POST
@login_required(login_url="/auth/login/")
def mark_all_notifications_as_read_view(request):
    """Marca como leidas todas las notificaciones del usuario actual."""

    mark_all_notifications_as_read(request.user)
    return redirect(_get_notifications_redirect_target(request))
