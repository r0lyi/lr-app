"""Tests del bloque inicial de administracion: home y listado de usuarios."""

from datetime import date

from django.urls import reverse

from apps.employees.models import Employee
from apps.users.models import User
from apps.vacations.models import VacationRequest

from .base import DashboardRoleBaseTestCase


class AdminUsersTests(DashboardRoleBaseTestCase):
    """Comprueba el resumen admin y la lista basica de usuarios."""

    def test_admin_home_shows_summary_counts_and_users_link(self):
        admin = self.create_active_user(
            email="admin-summary@example.com",
            dni="56565656P",
        )
        admin.roles.set([self.admin_role])

        employee_user = self.create_active_user(
            email="employee-summary@example.com",
            dni="78787878K",
        )
        employee = self.create_employee_profile(employee_user)
        self.create_vacation_request(
            employee,
            status=self.pending_status,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 1),
            requested_days="1.00",
        )

        rrhh_user = self.create_active_user(
            email="rrhh-summary@example.com",
            dni="90909090A",
        )
        rrhh_user.roles.set([self.rrhh_role])

        self.client.force_login(admin)

        response = self.client.get(reverse("dashboard:admin-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resumen general")
        self.assertContains(response, "Total usuarios")
        self.assertContains(response, "Usuarios activos")
        self.assertContains(response, "Fichas de empleado")
        self.assertContains(response, "Solicitudes registradas")
        self.assertContains(response, reverse("dashboard:admin-users"))
        self.assertEqual(response.context["total_users"], User.objects.count())
        self.assertEqual(
            response.context["active_users"],
            User.objects.filter(is_active=True).count(),
        )
        self.assertEqual(
            response.context["total_employee_profiles"],
            Employee.objects.count(),
        )
        self.assertEqual(
            response.context["total_vacation_requests"],
            VacationRequest.objects.count(),
        )
        self.assertEqual(
            response.context["total_rrhh_users"],
            User.objects.filter(roles__name="rrhh").distinct().count(),
        )
        self.assertEqual(
            response.context["total_admin_users"],
            User.objects.filter(roles__name="admin").distinct().count(),
        )

    def test_admin_users_page_lists_basic_user_data(self):
        admin = self.create_active_user(
            email="admin-users-list@example.com",
            dni="23232323T",
        )
        admin.roles.set([self.admin_role])

        employee_user = self.create_active_user(
            email="ana.lopez@example.com",
            dni="45454545J",
        )
        self.create_employee_profile(
            employee_user,
            first_name="Ana",
            last_name="Lopez",
        )

        rrhh_user = self.create_active_user(
            email="rrhh-users-list@example.com",
            dni="67676767A",
        )
        rrhh_user.roles.set([self.rrhh_role])

        inactive_user = self.create_active_user(
            email="inactive-users-list@example.com",
            dni="89898989Q",
        )
        inactive_user.is_active = False
        inactive_user.save(update_fields=["is_active"])

        self.client.force_login(admin)

        response = self.client.get(reverse("dashboard:admin-users"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuarios del sistema")
        self.assertContains(response, "Ana Lopez")
        self.assertContains(response, "ana.lopez@example.com")
        self.assertContains(response, "45454545J")
        self.assertContains(response, "Empleado")
        self.assertContains(response, "RRHH")
        self.assertContains(response, "Administrador")
        self.assertContains(response, "Activo")
        self.assertContains(response, "Inactivo")
        self.assertContains(response, "Si")
        self.assertContains(response, "No")
        self.assertContains(
            response,
            reverse("dashboard:admin-user-primary-role", args=[employee_user.pk]),
        )
        self.assertEqual(response.context["managed_users_count"], User.objects.count())

    def test_admin_can_change_the_primary_role_from_users_list(self):
        admin = self.create_active_user(
            email="admin-change-role@example.com",
            dni="15151515N",
        )
        admin.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="target-change-role@example.com",
            dni="26262626F",
        )
        target_user.roles.set([self.rrhh_role])

        self.client.force_login(admin)

        response = self.client.post(
            reverse("dashboard:admin-user-primary-role", args=[target_user.pk]),
            {"primary_role": self.employee_role.pk},
        )

        self.assertRedirects(response, reverse("dashboard:admin-users"))
        target_user.refresh_from_db()
        self.assertEqual(
            list(target_user.roles.values_list("name", flat=True)),
            ["employee"],
        )
