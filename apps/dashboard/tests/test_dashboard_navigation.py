"""Tests del menu lateral mostrado en cada panel del dashboard."""

from django.urls import reverse

from apps.notifications.models import Notification

from .base import DashboardRoleBaseTestCase


class DashboardNavigationTests(DashboardRoleBaseTestCase):
    """Verifica que cada panel renderiza el nav que le corresponde."""

    def test_each_panel_renders_the_nav_for_its_role(self):
        employee = self.create_active_user(
            email="employee-nav@example.com",
            dni="55555555K",
        )
        self.create_employee_profile(employee)

        rrhh = self.create_active_user(
            email="rrhh-nav@example.com",
            dni="66666666Q",
        )
        rrhh.roles.set([self.rrhh_role])

        admin = self.create_active_user(
            email="admin-nav@example.com",
            dni="77777777B",
        )
        admin.roles.set([self.admin_role])

        self.client.force_login(employee)
        employee_home = self.client.get(reverse("dashboard:employee-home"))
        self.assertContains(employee_home, reverse("dashboard:employee-home"))
        self.assertContains(employee_home, reverse("vacations:create-request"))
        self.assertContains(employee_home, reverse("employees:profile"))
        self.assertNotContains(employee_home, reverse("dashboard:admin-home"))

        self.client.force_login(rrhh)
        rrhh_home = self.client.get(reverse("dashboard:rrhh-home"))
        self.assertContains(rrhh_home, reverse("dashboard:rrhh-home"))
        self.assertContains(rrhh_home, reverse("audit:export-history"))
        self.assertContains(rrhh_home, reverse("employees:profile"))
        self.assertNotContains(rrhh_home, reverse("dashboard:employee-home"))

        self.client.force_login(admin)
        admin_home = self.client.get(reverse("dashboard:admin-home"))
        self.assertContains(admin_home, reverse("dashboard:admin-home"))
        self.assertContains(admin_home, reverse("employees:profile"))
        self.assertNotContains(admin_home, reverse("dashboard:rrhh-home"))

    def test_dashboard_header_renders_notification_dropdown(self):
        employee = self.create_active_user(
            email="employee-notifications@example.com",
            dni="12345678Z",
        )
        self.create_employee_profile(employee)
        Notification.objects.create(
            user=employee,
            notification_type=Notification.Type.VACATION_INFO,
            message="Tienes una nueva notificacion de prueba para el inbox.",
            is_read=False,
        )

        self.client.force_login(employee)

        response = self.client.get(reverse("dashboard:employee-home"))

        self.assertContains(response, "dash-notifications__button")
        self.assertContains(response, "Panel de notificaciones")
        self.assertContains(
            response,
            "Tienes una nueva notificacion de prueba para el inbox.",
        )
