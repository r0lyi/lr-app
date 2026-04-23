"""Administracion interna de notificaciones."""

from django.contrib import admin, messages
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Permite revisar y mantener el inbox interno del sistema."""

    list_display = (
        "id",
        "title_display",
        "notification_type",
        "user",
        "created_by",
        "is_read",
        "sent_at",
    )
    list_filter = (
        "notification_type",
        "is_read",
        "sent_at",
        "created_by",
    )
    search_fields = (
        "title",
        "message",
        "user__email",
        "user__dni",
        "created_by__email",
        "vacation_request__employee__first_name",
        "vacation_request__employee__last_name",
    )
    autocomplete_fields = ("user", "created_by", "vacation_request")
    readonly_fields = ("sent_at", "created_at")
    date_hierarchy = "sent_at"
    ordering = ("-sent_at",)
    save_on_top = True
    list_per_page = 25
    actions = ("mark_as_read", "mark_as_unread")
    fieldsets = (
        (
            gettext_lazy("Destino"),
            {
                "fields": (
                    "user",
                    "created_by",
                    "notification_type",
                    "is_read",
                )
            },
        ),
        (
            gettext_lazy("Contenido"),
            {
                "fields": (
                    "title",
                    "message",
                )
            },
        ),
        (
            gettext_lazy("Contexto"),
            {
                "fields": (
                    "vacation_request",
                    "previous_status_name",
                )
            },
        ),
        (gettext_lazy("Fechas"), {"fields": ("sent_at", "created_at")}),
    )

    def get_queryset(self, request):
        """Carga relaciones frecuentes para que el listado sea fluido."""

        return (
            super()
            .get_queryset(request)
            .select_related("user", "created_by", "vacation_request")
        )

    @admin.display(description=gettext_lazy("Título"))
    def title_display(self, obj):
        """Usa un texto corto incluso si la notificacion no tiene titulo."""

        return obj.title or obj.message[:60]

    @admin.action(description=gettext_lazy("Marcar como leídas"))
    def mark_as_read(self, request, queryset):
        """Accion masiva para limpiar avisos del inbox."""

        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            _("%(updated)s notificación(es) marcada(s) como leídas.")
            % {"updated": updated},
            level=messages.SUCCESS,
        )

    @admin.action(description=gettext_lazy("Marcar como no leídas"))
    def mark_as_unread(self, request, queryset):
        """Accion masiva para reabrir avisos del inbox."""

        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            _("%(updated)s notificación(es) marcada(s) como no leídas.")
            % {"updated": updated},
            level=messages.SUCCESS,
        )
