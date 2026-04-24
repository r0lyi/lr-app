"""Tests del formulario de onboarding de empleados."""

from django.test import TestCase
from django.urls import reverse

from apps.employees.models import Employee
from apps.users.models import User


class EmployeeOnboardingViewTests(TestCase):
    """Valida los requisitos minimos del formulario de ficha inicial."""

    def test_onboarding_requires_all_fields_and_shows_global_message(self):
        user = User.objects.create_user(
            email="onboarding@example.com",
            dni="12345678Z",
            password="PruebaSegura123!",
            is_active=True,
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("employees:onboarding"),
            {
                "first_name": "Ana",
                "last_name": "Lopez",
                "email": "onboarding@example.com",
                "phone": "",
                "hire_date": "2024-01-15",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Employee.objects.filter(user=user).exists())
        self.assertIn("phone", response.context["form"].errors)
        self.assertContains(
            response,
            "Debes completar todos los campos obligatorios de la ficha de empleado.",
        )
