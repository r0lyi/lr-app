"""Administracion interna de empleados y departamentos."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.employees.models import Department, Employee
from apps.vacations.models import VacationRequest


class DepartmentEmployeeInline(admin.TabularInline):
    """Resumen rapido de empleados asociados al departamento."""

    model = Employee
    fields = ("first_name", "last_name", "user", "hire_date")
    readonly_fields = ("first_name", "last_name", "user", "hire_date")
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        """Los empleados se crean desde su propia ficha para evitar duplicados."""

        return False


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Gestiona departamentos aunque sigan ocultos en la interfaz principal."""

    list_display = ("name", "max_concurrent_absences", "employees_count")
    search_fields = ("name",)
    ordering = ("name",)
    inlines = (DepartmentEmployeeInline,)
    list_per_page = 25

    @admin.display(description=_("Empleados"))
    def employees_count(self, obj):
        """Muestra cuantos empleados pertenecen al departamento."""

        return obj.employees.count()


class EmployeeVacationRequestInline(admin.TabularInline):
    """Solicitudes del empleado visibles desde su ficha."""

    model = VacationRequest
    fields = (
        "status",
        "start_date",
        "end_date",
        "requested_days",
        "request_date",
    )
    readonly_fields = (
        "status",
        "start_date",
        "end_date",
        "requested_days",
        "request_date",
    )
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        """Las solicitudes se gestionan desde el admin de vacaciones."""

        return False


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Ficha operativa del empleado para RRHH y administracion interna."""

    list_display = (
        "full_name",
        "user_email",
        "user_dni",
        "department",
        "hire_date",
        "available_days",
        "taken_days",
        "vacation_requests_count",
    )
    list_filter = ("department", "hire_date", "created_at")
    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "user__email",
        "user__dni",
        "department__name",
    )
    autocomplete_fields = ("user", "department")
    readonly_fields = ("created_at",)
    date_hierarchy = "hire_date"
    ordering = ("last_name", "first_name")
    save_on_top = True
    list_per_page = 25
    inlines = (EmployeeVacationRequestInline,)
    fieldsets = (
        (
            _("Identidad"),
            {
                "fields": (
                    "user",
                    "first_name",
                    "last_name",
                    "phone",
                )
            },
        ),
        (
            _("Organización"),
            {
                "fields": (
                    "department",
                    "hire_date",
                )
            },
        ),
        (
            _("Vacaciones"),
            {
                "fields": (
                    "available_days",
                    "taken_days",
                )
            },
        ),
        (_("Auditoría"), {"fields": ("created_at",)}),
    )

    def get_queryset(self, request):
        """Evita consultas repetidas en listados grandes."""

        return super().get_queryset(request).select_related("user", "department")

    @admin.display(description=_("Empleado"), ordering="last_name")
    def full_name(self, obj):
        """Nombre completo del empleado."""

        return str(obj)

    @admin.display(description=_("Correo"), ordering="user__email")
    def user_email(self, obj):
        """Correo del usuario asociado."""

        return obj.user.email

    @admin.display(description=_("DNI"), ordering="user__dni")
    def user_dni(self, obj):
        """DNI del usuario asociado."""

        return obj.user.dni

    @admin.display(description=_("Solicitudes"))
    def vacation_requests_count(self, obj):
        """Total de solicitudes registradas para el empleado."""

        return obj.vacation_requests.count()
