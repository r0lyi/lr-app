"""Base comun para los tests del dominio de vacaciones."""

from datetime import date

from django.test import TestCase

from apps.employees.models import Department, Employee
from apps.users.models import User


class VacationBaseTestCase(TestCase):
    """Helpers para crear un empleado autenticable con su perfil interno."""

    def create_employee_user(
        self,
        *,
        email,
        dni,
        hire_date=date(2024, 1, 15),
        first_name="Ana",
        last_name="Lopez",
        department=None,
    ):
        """Crea un usuario activo con rol employee por defecto y su perfil."""
        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        employee = Employee.objects.create(
            user=user,
            department=department,
            first_name=first_name,
            last_name=last_name,
            phone="600123123",
            hire_date=hire_date,
        )
        return user, employee

    def create_department(self, *, name="Limpieza", max_concurrent_absences=1):
        """Crea un departamento util para pruebas del dominio vacations."""

        return Department.objects.create(
            name=name,
            max_concurrent_absences=max_concurrent_absences,
        )
