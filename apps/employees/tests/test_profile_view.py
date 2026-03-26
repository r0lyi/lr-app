"""Tests de la vista basica de perfil del dominio employees."""

from django.test import TestCase
from django.urls import reverse

from apps.employees.models import Employee
from apps.users.models import Role, User


class EmployeeProfileViewTests(TestCase):
    """Comprueba el acceso y el contenido minimo del perfil."""

    @classmethod
    def setUpTestData(cls):
        cls.admin_role = Role.objects.get(name="admin")

    def create_user_with_profile(self, *, email, dni):
        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        profile = Employee.objects.create(
            user=user,
            first_name="Ana",
            last_name="Lopez",
            phone="600123123",
            hire_date="2024-01-15",
            available_days=30,
            taken_days=5,
        )
        return user, profile

    def test_employee_profile_view_shows_employee_information(self):
        user, _profile = self.create_user_with_profile(
            email="employee-profile@example.com",
            dni="12345678Z",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("employees:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Perfil")
        self.assertContains(response, "Ana")
        self.assertContains(response, "Lopez")
        self.assertContains(response, "employee-profile@example.com")
        self.assertContains(response, "600123123")
        self.assertContains(response, "15-01-2024")
        self.assertContains(response, "30")
        self.assertContains(response, "5")

    def test_admin_without_employee_profile_sees_clear_message(self):
        user = User.objects.create_user(
            email="admin-profile@example.com",
            dni="22222222J",
            password="PruebaSegura123!",
            is_active=True,
        )
        user.roles.set([self.admin_role])

        self.client.force_login(user)

        response = self.client.get(reverse("employees:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "No existe una ficha de empleado asociada a este usuario.",
        )
        self.assertContains(response, "admin-profile@example.com")
        self.assertContains(response, "Administrador")
