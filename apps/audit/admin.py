"""Administracion de auditoria y exportaciones."""

from django.contrib import admin

from apps.audit.models import AuditLog, ExportHistory


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Historial de auditoria consultable y protegido."""

    list_display = (
        "created_at",
        "user",
        "action_label",
        "resource_type",
        "resource_id",
        "description_preview",
    )
    list_filter = ("action", "resource_type", "created_at")
    search_fields = (
        "user__email",
        "user__dni",
        "action",
        "resource_type",
        "description",
    )
    autocomplete_fields = ("user",)
    readonly_fields = (
        "user",
        "action",
        "resource_type",
        "resource_id",
        "description",
        "created_at",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25

    @admin.display(description="Detalle")
    def description_preview(self, obj):
        """Resumen compacto para el listado."""

        description = obj.description or "Sin detalle"
        return description if len(description) <= 90 else f"{description[:90]}..."

    def has_add_permission(self, request):
        """Los logs se escriben desde servicios del sistema."""

        return False

    def has_change_permission(self, request, obj=None):
        """La auditoria debe ser inmutable."""

        return False

    def has_delete_permission(self, request, obj=None):
        """Evita borrar trazabilidad administrativa."""

        return False


@admin.register(ExportHistory)
class ExportHistoryAdmin(admin.ModelAdmin):
    """Historico consultable de exportaciones generadas."""

    list_display = (
        "created_at",
        "user",
        "export_type",
        "status",
        "total_records",
        "file_name",
    )
    list_filter = ("export_type", "status", "created_at", "user")
    search_fields = (
        "user__email",
        "user__dni",
        "file_name",
        "file_path",
        "export_type",
        "status",
    )
    autocomplete_fields = ("user",)
    readonly_fields = (
        "user",
        "file_name",
        "file_path",
        "filters_json",
        "total_records",
        "export_type",
        "status",
        "created_at",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25

    def has_add_permission(self, request):
        """Las exportaciones se generan desde los flujos de la app."""

        return False

    def has_change_permission(self, request, obj=None):
        """Protege la evidencia de exportaciones realizadas."""

        return False
