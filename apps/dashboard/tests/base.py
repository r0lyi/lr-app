"""Base compartida para los tests del dashboard segun rol."""

from datetime import date

from django.test import TestCase

from apps.employees.models import Employee
from apps.users.models import Role, User


class DashboardRoleBaseTestCase(TestCase):
    """Helpers comunes para crear usuarios y perfiles por rol."""

    @classmethod
    def setUpTestData(cls):
        """Carga el catalogo base de roles una sola vez por clase."""
        cls.employee_role = Role.objects.get(name="employee")
        cls.rrhh_role = Role.objects.get(name="rrhh")
        cls.admin_role = Role.objects.get(name="admin")

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
