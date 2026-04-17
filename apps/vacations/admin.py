"""Administracion interna del dominio de vacaciones."""

from django.contrib import admin, messages
from django.utils import timezone

from apps.vacations.models import (
    VacationRequest,
    VacationRequestHistory,
    VacationStatus,
)
from apps.vacations.services.requests.validators import calculate_requested_natural_days


@admin.register(VacationStatus)
class VacationStatusAdmin(admin.ModelAdmin):
    """Catalogo funcional de estados de una solicitud."""

    list_display = ("name", "display_label", "requests_count")
    search_fields = ("name",)
    ordering = ("name",)

    @admin.display(description="Etiqueta")
    def display_label(self, obj):
        """Muestra la etiqueta traducida usada por el sistema."""

        return str(obj)

    @admin.display(description="Solicitudes")
    def requests_count(self, obj):
        """Cantidad de solicitudes en ese estado."""

        return obj.vacation_requests.count()


class VacationRequestHistoryInline(admin.TabularInline):
    """Trazabilidad visible dentro de cada solicitud."""

    model = VacationRequestHistory
    fields = (
        "previous_status",
        "new_status",
        "changed_by",
        "change_date",
        "comment",
    )
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        """El historial se genera desde cambios de estado, no manualmente."""

        return False


@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    """Gestion completa de solicitudes para soporte interno y RRHH."""

    list_display = (
        "id",
        "employee",
        "status",
        "start_date",
        "end_date",
        "requested_days",
        "request_date",
        "resolution_date",
        "resolved_by",
    )
    list_filter = (
        "status",
        "employee__department",
        "start_date",
        "end_date",
        "request_date",
        "resolution_date",
        "reprogram_reason",
        "resolved_by",
    )
    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__user__email",
        "employee__user__dni",
        "employee_comment",
        "hr_comment",
    )
    autocomplete_fields = ("employee", "status", "resolved_by")
    readonly_fields = (
        "requested_days",
        "request_date",
        "resolution_date",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "request_date"
    ordering = ("-request_date",)
    save_on_top = True
    list_per_page = 25
    inlines = (VacationRequestHistoryInline,)
    actions = (
        "mark_as_approved",
        "mark_as_rejected",
        "mark_as_pending",
    )
    fieldsets = (
        (
            "Empleado y estado",
            {
                "fields": (
                    "employee",
                    "status",
                    "resolved_by",
                    "resolution_date",
                )
            },
        ),
        (
            "Periodo solicitado",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "requested_days",
                    "request_date",
                )
            },
        ),
        (
            "Comentarios",
            {
                "fields": (
                    "employee_comment",
                    "hr_comment",
                    "reprogram_reason",
                )
            },
        ),
        ("Auditoría", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Optimiza relaciones usadas en tabla y filtros."""

        return (
            super()
            .get_queryset(request)
            .select_related(
                "employee",
                "employee__user",
                "employee__department",
                "status",
                "resolved_by",
            )
        )

    def save_model(self, request, obj, form, change):
        """Recalcula días y deja coherente resolución al guardar desde admin."""

        previous_status = None
        if change and obj.pk:
            previous_status = (
                VacationRequest.objects.select_related("status")
                .filter(pk=obj.pk)
                .first()
            )

        obj.requested_days = calculate_requested_natural_days(
            obj.start_date,
            obj.end_date,
        )
        if obj.status and obj.status.name != "pending":
            obj.resolution_date = obj.resolution_date or timezone.now()
            obj.resolved_by = obj.resolved_by or request.user
        else:
            obj.resolution_date = None
            obj.resolved_by = None

        super().save_model(request, obj, form, change)

        previous_status_obj = previous_status.status if previous_status else None
        if previous_status_obj != obj.status:
            VacationRequestHistory.objects.create(
                vacation_request=obj,
                previous_status=previous_status_obj,
                new_status=obj.status,
                changed_by=request.user,
                comment="Cambio guardado desde Django Admin.",
            )

    @admin.action(description="Marcar como aprobadas")
    def mark_as_approved(self, request, queryset):
        """Accion masiva para aprobar solicitudes seleccionadas."""

        self._mark_with_status(request, queryset, "approved")

    @admin.action(description="Marcar como rechazadas")
    def mark_as_rejected(self, request, queryset):
        """Accion masiva para rechazar solicitudes seleccionadas."""

        self._mark_with_status(request, queryset, "rejected")

    @admin.action(description="Devolver a pendiente")
    def mark_as_pending(self, request, queryset):
        """Accion masiva para devolver solicitudes a revision."""

        self._mark_with_status(request, queryset, "pending")

    def _mark_with_status(self, request, queryset, status_name):
        """Aplica un estado y crea historial por cada solicitud afectada."""

        status = VacationStatus.objects.filter(name=status_name).first()
        if status is None:
            self.message_user(
                request,
                f"No existe el estado interno '{status_name}'.",
                level=messages.ERROR,
            )
            return

        updated_count = 0
        for vacation_request in queryset.select_related("status"):
            previous_status = vacation_request.status
            if previous_status == status:
                continue

            vacation_request.status = status
            if status.name == "pending":
                vacation_request.resolution_date = None
                vacation_request.resolved_by = None
            else:
                vacation_request.resolution_date = timezone.now()
                vacation_request.resolved_by = request.user
            vacation_request.save(
                update_fields=[
                    "status",
                    "resolution_date",
                    "resolved_by",
                    "updated_at",
                ]
            )
            VacationRequestHistory.objects.create(
                vacation_request=vacation_request,
                previous_status=previous_status,
                new_status=status,
                changed_by=request.user,
                comment="Cambio masivo aplicado desde Django Admin.",
            )
            updated_count += 1

        self.message_user(
            request,
            f"{updated_count} solicitud(es) actualizada(s).",
            level=messages.SUCCESS,
        )


@admin.register(VacationRequestHistory)
class VacationRequestHistoryAdmin(admin.ModelAdmin):
    """Consulta de cambios de estado de solicitudes."""

    list_display = (
        "vacation_request",
        "previous_status",
        "new_status",
        "changed_by",
        "change_date",
    )
    list_filter = ("previous_status", "new_status", "changed_by", "change_date")
    search_fields = (
        "vacation_request__employee__first_name",
        "vacation_request__employee__last_name",
        "vacation_request__employee__user__email",
        "comment",
    )
    autocomplete_fields = (
        "vacation_request",
        "previous_status",
        "new_status",
        "changed_by",
    )
    readonly_fields = (
        "vacation_request",
        "previous_status",
        "new_status",
        "changed_by",
        "change_date",
        "comment",
        "created_at",
    )
    date_hierarchy = "change_date"
    ordering = ("-change_date",)
    list_per_page = 25

    def has_add_permission(self, request):
        """El historial no debe crearse manualmente."""

        return False

    def has_change_permission(self, request, obj=None):
        """El historial se mantiene inmutable desde admin."""

        return False

    def has_delete_permission(self, request, obj=None):
        """Protege la trazabilidad de cambios de estado."""

        return False
