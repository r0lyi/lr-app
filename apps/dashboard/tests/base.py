"""Base compartida para los tests del dashboard segun rol."""

from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.employees.models import Department, Employee
from apps.vacations.models import VacationRequest, VacationStatus
from apps.users.models import Role, User


class DashboardRoleBaseTestCase(TestCase):
    """Helpers comunes para crear usuarios y perfiles por rol."""

    @classmethod
    def setUpTestData(cls):
        """Carga el catalogo base de roles una sola vez por clase."""
        cls.employee_role = Role.objects.get(name="employee")
        cls.rrhh_role = Role.objects.get(name="rrhh")
        cls.admin_role = Role.objects.get(name="admin")
        cls.pending_status = VacationStatus.objects.get(name="pending")
        cls.approved_status = VacationStatus.objects.get(name="approved")
        cls.rejected_status = VacationStatus.objects.get(name="rejected")

    def create_active_user(self, *, email, dni):
        """Crea un usuario activo listo para iniciar sesion en tests."""
        return User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )

    def create_employee_profile(
        self,
        user,
        *,
        first_name="Ana",
        last_name="Lopez",
        phone="600123123",
        hire_date=date(2024, 1, 15),
    ):
        """Crea la ficha Employee necesaria para el panel de empleado."""
        return Employee.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            hire_date=hire_date,
        )

    def create_department(self, *, name="Limpieza", max_concurrent_absences=1):
        """Crea un departamento reutilizable para pruebas administrativas."""

        return Department.objects.create(
            name=name,
            max_concurrent_absences=max_concurrent_absences,
        )

    def create_vacation_request(
        self,
        employee,
        *,
        status,
        start_date,
        end_date,
        requested_days,
        employee_comment="",
    ):
        """Crea solicitudes de vacaciones de prueba para filtros y listados."""
        return VacationRequest.objects.create(
            employee=employee,
            status=status,
            start_date=start_date,
            end_date=end_date,
            requested_days=Decimal(requested_days),
            employee_comment=employee_comment or None,
        )
