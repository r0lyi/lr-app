from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.employees.models import Employee
from apps.users.models import Role, User


class DashboardRoleRoutingTests(TestCase):
    """Comprueba el enrutado basico del dashboard segun el rol principal."""

    @classmethod
    def setUpTestData(cls):
        cls.rrhh_role = Role.objects.get(name="rrhh")
        cls.admin_role = Role.objects.get(name="admin")

    def create_active_user(self, *, email, dni):
        """Crea un usuario activo para las pruebas de rutas protegidas."""
        return User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )

    def test_employee_without_profile_is_redirected_to_onboarding(self):
        user = self.create_active_user(
            email="employee-no-profile@example.com",
            dni="12345678Z",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("employees:onboarding"))
        self.assertEqual(list(user.roles.values_list("name", flat=True)), ["employee"])

    def test_employee_with_profile_is_redirected_to_employee_home(self):
        user = self.create_active_user(
            email="employee-with-profile@example.com",
            dni="00000000T",
        )
        Employee.objects.create(
            user=user,
            first_name="Ana",
            last_name="Lopez",
            phone="600123123",
            hire_date=date(2024, 1, 15),
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:employee-home"))

        employee_home = self.client.get(reverse("dashboard:employee-home"))
        self.assertEqual(employee_home.status_code, 200)
        self.assertContains(employee_home, "Panel de empleado")
        self.assertContains(employee_home, "Ana")

    def test_rrhh_is_redirected_to_rrhh_home(self):
        user = self.create_active_user(
            email="rrhh@example.com",
            dni="11111111H",
        )
        user.roles.add(self.rrhh_role)

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:rrhh-home"))

        rrhh_home = self.client.get(reverse("dashboard:rrhh-home"))
        self.assertEqual(rrhh_home.status_code, 200)
        self.assertContains(rrhh_home, "Panel de RRHH")

    def test_admin_is_redirected_to_admin_home(self):
        user = self.create_active_user(
            email="admin@example.com",
            dni="22222222J",
        )
        user.roles.add(self.admin_role)

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:admin-home"))

        admin_home = self.client.get(reverse("dashboard:admin-home"))
        self.assertEqual(admin_home.status_code, 200)
        self.assertContains(admin_home, "Panel de administrador")
