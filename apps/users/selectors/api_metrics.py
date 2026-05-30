"""Consultas agregadas para endpoints API de usuarios."""

from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.db.models import Count
from django.utils import timezone

from apps.employees.models import Employee
from apps.employees.services.employee_dashboard import (
    calculate_annual_vacation_days_for_year,
)
from apps.users.models import User
from apps.vacations.models import VacationRequest
from apps.vacations.selectors import get_reserved_annual_vacation_days_for_year

from .roles import get_primary_role


def _decimal_to_string(value):
    """Normaliza decimales de dias para mantener precision en JSON."""

    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _count_users_on_vacation(today):
    """Cuenta usuarios con una solicitud aprobada que cubre la fecha actual."""

    return (
        User.objects.filter(
            employee_profile__vacation_requests__status__name="approved",
            employee_profile__vacation_requests__start_date__lte=today,
            employee_profile__vacation_requests__end_date__gte=today,
        )
        .distinct()
        .count()
    )


def get_user_kpis():
    """Devuelve metricas generales de usuarios y perfiles de empleado."""

    today = timezone.localdate()
    roles = (
        User.objects.values("roles__name")
        .annotate(total=Count("id", distinct=True))
        .order_by("roles__name")
    )

    return {
        "total_usuarios": User.objects.count(),
        "usuarios_activos": User.objects.filter(is_active=True).count(),
        "usuarios_inactivos": User.objects.filter(is_active=False).count(),
        "usuarios_en_vacaciones": _count_users_on_vacation(today),
        "usuarios_pendientes_activacion": User.objects.filter(
            is_active=False,
            password__startswith=UNUSABLE_PASSWORD_PREFIX,
        ).count(),
        "perfiles_empleado_totales": Employee.objects.count(),
        "usuarios_sin_perfil_empleado": User.objects.filter(
            employee_profile__isnull=True,
        ).count(),
        "usuarios_por_rol": {
            row["roles__name"]: row["total"]
            for row in roles
            if row["roles__name"]
        },
    }


def get_user_summary(user):
    """Devuelve el resumen completo de un usuario para API."""

    user = (
        User.objects.prefetch_related("roles")
        .select_related("employee_profile__department")
        .get(pk=user.pk)
    )
    role_names = [role.name for role in user.roles.all()]
    primary_role = get_primary_role(user)

    try:
        employee = user.employee_profile
    except Employee.DoesNotExist:
        employee = None

    if employee is None:
        return {
            "id": user.id,
            "email": user.email,
            "dni": user.dni,
            "is_active": user.is_active,
            "registered_at": user.registered_at,
            "rol": primary_role,
            "roles": role_names,
            "empleado": None,
            "dias_vacaciones": None,
            "solicitudes": {
                "total": 0,
                "pendientes": 0,
                "aprobadas": 0,
                "rechazadas": 0,
                "ultima_solicitud": None,
            },
        }

    current_year = timezone.localdate().year
    assigned_days = calculate_annual_vacation_days_for_year(
        employee.hire_date,
        year=current_year,
    )
    reserved_days = get_reserved_annual_vacation_days_for_year(
        employee,
        year=current_year,
    )
    remaining_days = max(assigned_days - reserved_days, Decimal("0.00"))
    requests = VacationRequest.objects.filter(employee=employee).select_related("status")
    latest_request = requests.order_by("-request_date", "-id").first()

    return {
        "id": user.id,
        "email": user.email,
        "dni": user.dni,
        "is_active": user.is_active,
        "registered_at": user.registered_at,
        "rol": primary_role,
        "roles": role_names,
        "empleado": {
            "id": employee.id,
            "nombre": employee.first_name,
            "apellido": employee.last_name,
            "nombre_completo": str(employee),
            "telefono": employee.phone,
            "fecha_contratacion": employee.hire_date,
            "departamento": (
                {
                    "id": employee.department.id,
                    "nombre": employee.department.name,
                }
                if employee.department
                else None
            ),
        },
        "dias_vacaciones": {
            "anio": current_year,
            "asignados": _decimal_to_string(assigned_days),
            "reservados": _decimal_to_string(reserved_days),
            "restantes": _decimal_to_string(remaining_days),
            "puede_solicitar_dias": _decimal_to_string(remaining_days),
        },
        "solicitudes": {
            "total": requests.count(),
            "pendientes": requests.filter(status__name="pending").count(),
            "aprobadas": requests.filter(status__name="approved").count(),
            "rechazadas": requests.filter(status__name="rejected").count(),
            "ultima_solicitud": _build_latest_request(latest_request),
        },
    }


def _build_latest_request(vacation_request):
    """Normaliza la ultima solicitud para el resumen de usuario."""

    if vacation_request is None:
        return None

    return {
        "id": vacation_request.id,
        "fecha_solicitud": vacation_request.request_date.date(),
        "fecha_inicio": vacation_request.start_date,
        "fecha_fin": vacation_request.end_date,
        "dias_solicitados": _decimal_to_string(vacation_request.requested_days),
        "estado": vacation_request.status.name,
        "estado_label": str(vacation_request.status),
    }
