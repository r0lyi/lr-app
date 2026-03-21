"""Tests de enrutado principal del dashboard segun el rol."""

from datetime import date

from django.urls import reverse

from .base import DashboardRoleBaseTestCase


class DashboardRoutingTests(DashboardRoleBaseTestCase):
    """Comprueba a que home se redirige desde dashboard:home."""

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
        self.create_employee_profile(user)

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:employee-home"))

        employee_home = self.client.get(reverse("dashboard:employee-home"))
        self.assertEqual(employee_home.status_code, 200)
        self.assertContains(employee_home, "Panel de empleado")
        self.assertContains(employee_home, "Ana")
        self.assertContains(employee_home, "Solicitudes pendientes: 0")
        self.assertContains(employee_home, "Derecho anual de vacaciones")
        self.assertContains(employee_home, "30.00")
        self.assertContains(employee_home, "Ultima resolucion:")
        self.assertContains(employee_home, "Ninguna")
        self.assertContains(employee_home, "No hay solicitudes registradas.")
        self.assertContains(employee_home, "Fecha inicio")
        self.assertContains(employee_home, "Fecha final")
        self.assertContains(employee_home, "Estado")
        self.assertContains(employee_home, "Filtrar")

    def test_employee_home_filters_requests_by_dates_and_status(self):
        user = self.create_active_user(
            email="employee-filter@example.com",
            dni="13579135G",
        )
        employee = self.create_employee_profile(user)
        self.create_vacation_request(
            employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )
        self.create_vacation_request(
            employee,
            status=self.approved_status,
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 12),
            requested_days="3.00",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("dashboard:employee-home"),
            {
                "start_date": "2026-08-01",
                "end_date": "2026-08-31",
                "status": "approved",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10/08/2026 - 12/08/2026")
        self.assertContains(response, "Estado: approved")
        self.assertNotContains(response, "01/07/2026 - 05/07/2026")

    def test_rrhh_is_redirected_to_rrhh_home(self):
        user = self.create_active_user(
            email="rrhh@example.com",
            dni="11111111H",
        )
        user.roles.set([self.rrhh_role])

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
        user.roles.set([self.admin_role])

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:admin-home"))

        admin_home = self.client.get(reverse("dashboard:admin-home"))
        self.assertEqual(admin_home.status_code, 200)
        self.assertContains(admin_home, "Panel de administrador")
