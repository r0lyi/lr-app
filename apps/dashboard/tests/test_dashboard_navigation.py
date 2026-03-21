"""Tests del menu lateral mostrado en cada panel del dashboard."""

from django.urls import reverse

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
        self.assertNotContains(employee_home, reverse("dashboard:admin-home"))

        self.client.force_login(rrhh)
        rrhh_home = self.client.get(reverse("dashboard:rrhh-home"))
        self.assertContains(rrhh_home, reverse("dashboard:rrhh-home"))
        self.assertNotContains(rrhh_home, reverse("dashboard:employee-home"))

        self.client.force_login(admin)
        admin_home = self.client.get(reverse("dashboard:admin-home"))
        self.assertContains(admin_home, reverse("dashboard:admin-home"))
        self.assertNotContains(admin_home, reverse("dashboard:rrhh-home"))
