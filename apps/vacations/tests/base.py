"""Base comun para los tests del dominio de vacaciones."""

from datetime import date

from django.test import TestCase

from apps.employees.models import Employee
from apps.users.models import User


class VacationBaseTestCase(TestCase):
    """Helpers para crear un empleado autenticable con su perfil interno."""

    def create_employee_user(self, *, email, dni):
        """Crea un usuario activo con rol employee por defecto y su perfil."""
        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        employee = Employee.objects.create(
            user=user,
            first_name="Ana",
            last_name="Lopez",
            phone="600123123",
            hire_date=date(2024, 1, 15),
        )
        return user, employee
