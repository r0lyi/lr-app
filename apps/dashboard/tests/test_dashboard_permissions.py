"""Tests de proteccion de paneles segun el rol del usuario."""

from datetime import date

from django.urls import reverse

from .base import DashboardRoleBaseTestCase


class DashboardPermissionTests(DashboardRoleBaseTestCase):
    """Comprueba que cada rol solo entra a los paneles permitidos."""

    def test_employee_cannot_open_rrhh_panel(self):
        user = self.create_active_user(
            email="employee-panel@example.com",
            dni="33333333P",
        )
        self.create_employee_profile(
            user,
            first_name="Laura",
            last_name="Martin",
            hire_date=date(2023, 5, 10),
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:rrhh-home"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))

    def test_employee_cannot_open_admin_panel(self):
        user = self.create_active_user(
            email="employee-admin-block@example.com",
            dni="88888888Y",
        )
        self.create_employee_profile(
            user,
            first_name="Laura",
            last_name="Martin",
            hire_date=date(2023, 5, 10),
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:admin-home"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))

    def test_rrhh_cannot_open_admin_panel(self):
        user = self.create_active_user(
            email="rrhh-panel@example.com",
            dni="44444444A",
        )
        user.roles.set([self.rrhh_role])

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:admin-home"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))

    def test_admin_can_open_admin_and_rrhh_panels(self):
        user = self.create_active_user(
            email="admin-protected@example.com",
            dni="99999999R",
        )
        user.roles.set([self.admin_role])

        self.client.force_login(user)

        admin_response = self.client.get(reverse("dashboard:admin-home"))
        rrhh_response = self.client.get(reverse("dashboard:rrhh-home"))

        self.assertEqual(admin_response.status_code, 200)
        self.assertContains(admin_response, "Panel de administrador")
        self.assertEqual(rrhh_response.status_code, 200)
        self.assertContains(rrhh_response, "Panel de RRHH")
