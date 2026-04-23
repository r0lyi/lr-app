"""Vista principal del panel de administracion."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.utils.decorators import role_required
from apps.notifications.forms import AdminBroadcastNotificationForm
from apps.notifications.selectors import get_admin_broadcast_notification_recipients
from apps.notifications.services import create_admin_broadcast_notifications
from apps.users.selectors import get_admin_dashboard_summary


@role_required("admin")
def admin_home_view(request):
    """Muestra un resumen general del sistema para el rol admin.

    Esta home no pretende sustituir a las pantallas de gestion detallada. Su
    objetivo es ofrecer una fotografia general del sistema y un acceso rapido a
    la lista de usuarios, que es la primera herramienta util para un admin.
    """
    broadcast_form = AdminBroadcastNotificationForm()
    summary = get_admin_dashboard_summary()

    if request.method == "POST":
        broadcast_form = AdminBroadcastNotificationForm(request.POST)
        if broadcast_form.is_valid():
            notifications = create_admin_broadcast_notifications(
                sender=request.user,
                title=broadcast_form.cleaned_data["title"],
                message=broadcast_form.cleaned_data["message"],
            )
            messages.success(
                request,
                _("Se ha enviado un aviso general a %(count)s usuario(s).")
                % {"count": len(notifications)},
            )
            return redirect("dashboard:admin-home")

    recipients_count = get_admin_broadcast_notification_recipients().count()
    summary_cards = [
        {
            "label": gettext_lazy("Total usuarios"),
            "value": summary["total_users"],
            "icon": "users",
            "tone": "blue",
        },
        {
            "label": gettext_lazy("Usuarios empleados"),
            "value": summary["total_employee_users"],
            "icon": "id-card",
            "tone": "green",
        },
        {
            "label": gettext_lazy("Usuarios RRHH"),
            "value": summary["total_rrhh_users"],
            "icon": "users",
            "tone": "orange",
        },
        {
            "label": gettext_lazy("Admins"),
            "value": summary["total_admin_users"],
            "icon": "shield",
            "tone": "dark",
        },
    ]

    return render(
        request,
        "dashboard/pages/admin_home.html",
        build_dashboard_base_context(
            request.user,
            "admin",
            request=request,
            active_section="home",
            extra_context={
                **summary,
                "admin_summary_cards": summary_cards,
                "broadcast_notification_form": broadcast_form,
                "broadcast_recipients_count": recipients_count,
            },
        ),
    )
