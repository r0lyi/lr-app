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
        department = self.create_department(name="Operaciones")
        employee_profile = self.create_employee_profile(
            employee_user,
            first_name="Ana",
            last_name="Lopez",
        )
        employee_profile.department = department
        employee_profile.save(update_fields=["department"])

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
        self.assertContains(response, "Operaciones")
        self.assertContains(response, "RRHH")
        self.assertContains(response, "Administrador")
        self.assertContains(response, "Acceso activo")
        self.assertContains(response, "Acceso desactivado")
        self.assertContains(
            response,
            reverse("dashboard:admin-user-edit", args=[employee_user.pk]),
        )
        self.assertContains(response, "Editar usuario")
        self.assertEqual(response.context["managed_users_count"], User.objects.count())

    def test_admin_can_open_edit_user_page(self):
        admin = self.create_active_user(
            email="admin-edit-user@example.com",
            dni="15151515N",
        )
        admin.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="edit-user@example.com",
            dni="26262626F",
        )
        employee_profile = self.create_employee_profile(
            target_user,
            first_name="Clara",
            last_name="Diaz",
        )
        department = self.create_department(name="Finanzas")
        employee_profile.department = department
        employee_profile.save(update_fields=["department"])

        self.client.force_login(admin)

        response = self.client.get(
            reverse("dashboard:admin-user-edit", args=[target_user.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editar usuario")
        self.assertContains(response, "Clara Diaz")
        self.assertContains(response, "Finanzas")
        self.assertContains(
            response,
            reverse("dashboard:admin-user-primary-role", args=[target_user.pk]),
        )
        self.assertContains(
            response,
            reverse("dashboard:admin-user-department", args=[target_user.pk]),
        )
        self.assertContains(
            response,
            reverse("dashboard:admin-user-access-state", args=[target_user.pk]),
        )

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

    def test_admin_can_change_primary_role_and_return_to_edit_page(self):
        admin = self.create_active_user(
            email="admin-change-role-edit@example.com",
            dni="13131313S",
        )
        admin.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="target-change-role-edit@example.com",
            dni="24242424X",
        )
        target_user.roles.set([self.employee_role])

        self.client.force_login(admin)

        response = self.client.post(
            reverse("dashboard:admin-user-primary-role", args=[target_user.pk]),
            {
                "primary_role": self.rrhh_role.pk,
                "next": reverse("dashboard:admin-user-edit", args=[target_user.pk]),
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:admin-user-edit", args=[target_user.pk]),
        )
        target_user.refresh_from_db()
        self.assertEqual(
            list(target_user.roles.values_list("name", flat=True)),
            ["rrhh"],
        )

    def test_admin_can_deactivate_a_user_from_users_list(self):
        admin = self.create_active_user(
            email="admin-change-active@example.com",
            dni="13131313S",
        )
        admin.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="target-change-active@example.com",
            dni="24242424X",
        )

        self.client.force_login(admin)

        response = self.client.post(
            reverse("dashboard:admin-user-access-state", args=[target_user.pk]),
            {"is_active": "0"},
        )

        self.assertRedirects(response, reverse("dashboard:admin-users"))
        target_user.refresh_from_db()
        self.assertFalse(target_user.is_active)

    def test_admin_can_change_department_from_users_list(self):
        admin = self.create_active_user(
            email="admin-change-department@example.com",
            dni="56565656P",
        )
        admin.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="target-change-department@example.com",
            dni="78787878K",
        )
        employee_profile = self.create_employee_profile(target_user)
        previous_department = self.create_department(name="Limpieza")
        new_department = self.create_department(name="Mantenimiento")
        employee_profile.department = previous_department
        employee_profile.save(update_fields=["department"])

        self.client.force_login(admin)

        response = self.client.post(
            reverse("dashboard:admin-user-department", args=[target_user.pk]),
            {"department": new_department.pk},
        )

        self.assertRedirects(response, reverse("dashboard:admin-users"))
        employee_profile.refresh_from_db()
        self.assertEqual(employee_profile.department, new_department)
