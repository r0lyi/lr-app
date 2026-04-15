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

    def test_employee_cannot_open_admin_users_panel(self):
        user = self.create_active_user(
            email="employee-admin-users-block@example.com",
            dni="12121212M",
        )
        self.create_employee_profile(user)

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:admin-users"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))

    def test_employee_cannot_open_admin_user_edit_panel(self):
        user = self.create_active_user(
            email="employee-admin-user-edit-block@example.com",
            dni="56565656P",
        )
        self.create_employee_profile(user)

        target_user = self.create_active_user(
            email="target-admin-user-edit-block@example.com",
            dni="78787878K",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("dashboard:admin-user-edit", args=[target_user.pk]),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))

    def test_rrhh_cannot_open_admin_users_panel(self):
        user = self.create_active_user(
            email="rrhh-admin-users-block@example.com",
            dni="34343434H",
        )
        user.roles.set([self.rrhh_role])

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:admin-users"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))

    def test_admin_can_open_admin_and_requests_panels(self):
        user = self.create_active_user(
            email="admin-protected@example.com",
            dni="99999999R",
        )
        user.roles.set([self.admin_role])
        self.create_employee_profile(user)

        self.client.force_login(user)

        admin_response = self.client.get(reverse("dashboard:admin-home"))
        admin_requests_response = self.client.get(reverse("dashboard:admin-requests"))
        admin_users_response = self.client.get(reverse("dashboard:admin-users"))
        rrhh_response = self.client.get(reverse("dashboard:rrhh-home"))
        request_response = self.client.get(reverse("vacations:create-request"))

        self.assertEqual(admin_response.status_code, 200)
        self.assertContains(admin_response, "Aviso general")
        self.assertEqual(admin_requests_response.status_code, 200)
        self.assertContains(admin_requests_response, "Solicitudes")
        self.assertEqual(admin_users_response.status_code, 200)
        self.assertContains(admin_users_response, "Gestión de Usuarios")
        self.assertEqual(rrhh_response.status_code, 302)
        self.assertEqual(rrhh_response.url, reverse("dashboard:admin-requests"))
        self.assertEqual(request_response.status_code, 200)
        self.assertContains(request_response, "Solicitar vacaciones")

    def test_employee_cannot_change_roles_from_admin_users_panel(self):
        user = self.create_active_user(
            email="employee-admin-role-change@example.com",
            dni="37373737W",
        )
        self.create_employee_profile(user)

        target_user = self.create_active_user(
            email="target-admin-role-change@example.com",
            dni="48484848C",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("dashboard:admin-user-primary-role", args=[target_user.pk]),
            {"primary_role": self.rrhh_role.pk},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))
        target_user.refresh_from_db()
        self.assertEqual(
            list(target_user.roles.values_list("name", flat=True)),
            ["employee"],
        )

    def test_employee_cannot_change_access_state_from_admin_users_panel(self):
        user = self.create_active_user(
            email="employee-admin-active-change@example.com",
            dni="51515151G",
        )
        self.create_employee_profile(user)

        target_user = self.create_active_user(
            email="target-admin-active-change@example.com",
            dni="62626262E",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("dashboard:admin-user-access-state", args=[target_user.pk]),
            {"is_active": "0"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))
        target_user.refresh_from_db()
        self.assertTrue(target_user.is_active)

    def test_employee_cannot_change_department_from_admin_users_panel(self):
        user = self.create_active_user(
            email="employee-admin-department-change@example.com",
            dni="90909090A",
        )
        self.create_employee_profile(user)

        target_user = self.create_active_user(
            email="target-admin-department-change@example.com",
            dni="23232323T",
        )
        employee_profile = self.create_employee_profile(target_user)
        previous_department = self.create_department(name="Limpieza")
        new_department = self.create_department(name="Mantenimiento")
        employee_profile.department = previous_department
        employee_profile.save(update_fields=["department"])

        self.client.force_login(user)

        response = self.client.post(
            reverse("dashboard:admin-user-department", args=[target_user.pk]),
            {"department": new_department.pk},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))
        employee_profile.refresh_from_db()
        self.assertEqual(employee_profile.department, previous_department)
