"""Tests del bloque inicial de administracion: home y listado de usuarios."""

from datetime import date

from django.core import mail
from django.test import override_settings
from django.urls import reverse

from apps.employees.models import Employee
from apps.notifications.models import Notification
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
        self.assertContains(response, "Total usuarios")
        self.assertContains(response, "Activos")
        self.assertContains(response, "Fichas emp.")
        self.assertContains(response, "Solicitudes")
        self.assertContains(response, "Aviso general")
        self.assertContains(response, "Comunicación Directa")
        self.assertContains(response, "Consejo Profesional")
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

    def test_admin_home_can_send_general_notification_to_all_active_users(self):
        admin = self.create_active_user(
            email="admin-broadcast-home@example.com",
            dni="31313131B",
        )
        admin.roles.set([self.admin_role])

        employee_user = self.create_active_user(
            email="employee-broadcast-home@example.com",
            dni="45454545J",
        )
        rrhh_user = self.create_active_user(
            email="rrhh-broadcast-home@example.com",
            dni="67676767A",
        )
        rrhh_user.roles.set([self.rrhh_role])

        self.client.force_login(admin)

        response = self.client.post(
            reverse("dashboard:admin-home"),
            {
                "title": "Aviso para toda la plantilla",
                "message": "El sistema estará en mantenimiento esta noche.",
            },
        )

        self.assertRedirects(response, reverse("dashboard:admin-home"))
        notifications = Notification.objects.filter(
            notification_type=Notification.Type.ADMIN_BROADCAST_MESSAGE
        )
        self.assertGreaterEqual(notifications.count(), 3)
        self.assertGreaterEqual(
            notifications.filter(created_by=admin).count(),
            3,
        )
        self.assertIn(admin.email, notifications.values_list("user__email", flat=True))
        self.assertIn(
            employee_user.email,
            notifications.values_list("user__email", flat=True),
        )
        self.assertIn(
            rrhh_user.email,
            notifications.values_list("user__email", flat=True),
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
        self.assertContains(response, "Gestión de Usuarios")
        self.assertContains(response, "Nuevo Usuario")
        self.assertContains(response, "Total Usuarios")
        self.assertContains(response, "Cuentas Activas")
        self.assertContains(response, "Cuentas Inactivas")
        self.assertContains(response, "Fichas de Empleado")
        self.assertContains(response, "Ana Lopez")
        self.assertContains(response, "ana.lopez@example.com")
        self.assertContains(response, "45454545J")
        self.assertContains(response, "Empleado")
        self.assertContains(response, "RRHH")
        self.assertContains(response, "Administrador")
        self.assertContains(response, "Acceso activo")
        self.assertContains(response, "Acceso desactivado")
        self.assertNotContains(response, "Departamento")
        self.assertContains(
            response,
            reverse("dashboard:admin-user-edit", args=[employee_user.pk]),
        )
        self.assertContains(response, "Editar usuario")
        self.assertEqual(response.context["managed_users_count"], User.objects.count())

    def test_admin_users_page_paginates_users_by_ten(self):
        admin = self.create_active_user(
            email="zz-admin-users-pagination@example.com",
            dni=self.build_valid_dni(31000000),
        )
        admin.roles.set([self.admin_role])
        for index in range(12):
            self.create_active_user(
                email=f"pagination-user-{index:02d}@example.com",
                dni=self.build_valid_dni(31000001 + index),
            )

        self.client.force_login(admin)

        first_page = self.client.get(reverse("dashboard:admin-users"))
        second_page = self.client.get(
            reverse("dashboard:admin-users"),
            {"page": "2"},
        )

        self.assertEqual(first_page.status_code, 200)
        expected_users_count = User.objects.count()
        self.assertEqual(first_page.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(first_page.context["managed_users_count"], expected_users_count)
        self.assertEqual(len(first_page.context["managed_users"]), 10)
        self.assertContains(
            first_page,
            f"Mostrando 1-10 de {expected_users_count} usuarios",
        )
        self.assertContains(first_page, 'href="?page=2"', html=False)

        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(
            len(second_page.context["managed_users"]),
            expected_users_count - 10,
        )
        self.assertContains(
            second_page,
            f"Mostrando 11-{expected_users_count} de {expected_users_count} usuarios",
        )

    @override_settings(
        EMAIL_PROVIDER="console",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="test@example.com",
        FRONTEND_URL="http://testserver",
    )
    def test_admin_users_page_can_create_new_user_from_modal(self):
        admin = self.create_active_user(
            email="admin-users-create@example.com",
            dni="92929292T",
        )
        admin.roles.set([self.admin_role])

        self.client.force_login(admin)
        mail.outbox.clear()

        response = self.client.post(
            reverse("dashboard:admin-users"),
            {
                "dni": "10101010P",
                "email": "nuevo.usuario@example.com",
            },
        )

        self.assertRedirects(response, reverse("dashboard:admin-users"))

        created_user = User.objects.get(email="nuevo.usuario@example.com")
        self.assertFalse(created_user.is_active)
        self.assertFalse(created_user.has_usable_password())
        self.assertTrue(created_user.activation_token)
        self.assertEqual(len(mail.outbox), 1)

    def test_admin_users_page_filters_by_search_role_and_access(self):
        admin = self.create_active_user(
            email="admin-users-filters@example.com",
            dni="15151515N",
        )
        admin.roles.set([self.admin_role])

        employee_user = self.create_active_user(
            email="laura.sanz@example.com",
            dni="26262626F",
        )
        self.create_employee_profile(
            employee_user,
            first_name="Laura",
            last_name="Sanz",
        )

        rrhh_user = self.create_active_user(
            email="manuel.rrhh@example.com",
            dni="13131313S",
        )
        rrhh_user.roles.set([self.rrhh_role])
        self.create_employee_profile(
            rrhh_user,
            first_name="Manuel",
            last_name="Lopez",
        )

        pending_user = self.create_active_user(
            email="pendiente@example.com",
            dni="24242424X",
        )
        pending_user.is_active = False
        pending_user.set_unusable_password()
        pending_user.save(update_fields=["is_active", "password"])

        self.client.force_login(admin)

        response = self.client.get(
            reverse("dashboard:admin-users"),
            {
                "search": "Laura",
                "primary_role": "employee",
                "access_state": "active",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laura Sanz")
        self.assertNotContains(response, "Manuel Lopez")
        self.assertNotContains(response, "pendiente@example.com")
        self.assertEqual(response.context["managed_users_count"], 1)

    def test_admin_users_page_can_filter_pending_activation_accounts(self):
        admin = self.create_active_user(
            email="admin-users-pending@example.com",
            dni="56565656P",
        )
        admin.roles.set([self.admin_role])

        active_user = self.create_active_user(
            email="active-users-filter@example.com",
            dni="78787878K",
        )

        pending_user = self.create_active_user(
            email="pending-users-filter@example.com",
            dni="90909090A",
        )
        pending_user.is_active = False
        pending_user.set_unusable_password()
        pending_user.save(update_fields=["is_active", "password"])

        self.client.force_login(admin)

        response = self.client.get(
            reverse("dashboard:admin-users"),
            {"access_state": "pending_activation"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "pending-users-filter@example.com")
        self.assertNotContains(response, "active-users-filter@example.com")

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
        self.create_employee_profile(
            target_user,
            first_name="Clara",
            last_name="Diaz",
        )

        self.client.force_login(admin)

        response = self.client.get(
            reverse("dashboard:admin-user-edit", args=[target_user.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editar usuario")
        self.assertContains(response, "Clara Diaz")
        self.assertContains(response, "Rol y estado")
        self.assertContains(response, "Nuevo rol principal")
        self.assertContains(response, "Estado de la cuenta")
        self.assertContains(response, "Guardar cambios")
        self.assertNotContains(response, "Departamento")
        self.assertNotContains(response, "Guardar departamento")
        self.assertContains(
            response,
            reverse("dashboard:admin-user-edit", args=[target_user.pk]),
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

    def test_admin_edit_modal_replaces_existing_roles(self):
        admin = self.create_active_user(
            email="admin-replace-role@example.com",
            dni="90909090A",
        )
        admin.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="target-replace-role@example.com",
            dni="32323232K",
        )
        target_user.roles.set([self.employee_role, self.rrhh_role])

        self.client.force_login(admin)

        edit_url = reverse("dashboard:admin-user-edit", args=[target_user.pk])
        response = self.client.post(
            edit_url,
            {
                "primary_role": self.admin_role.pk,
                "is_active": "true",
                "next": edit_url,
            },
        )

        self.assertRedirects(response, edit_url)
        target_user.refresh_from_db()
        self.assertEqual(
            list(target_user.roles.values_list("name", flat=True)),
            ["admin"],
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

    def test_admin_can_change_access_state_from_edit_page_with_boolean_values(self):
        admin = self.create_active_user(
            email="admin-edit-active-state@example.com",
            dni="34343434H",
        )
        admin.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="target-edit-active-state@example.com",
            dni="27272727V",
        )
        edit_url = reverse("dashboard:admin-user-edit", args=[target_user.pk])

        self.client.force_login(admin)

        response = self.client.post(
            edit_url,
            {
                "primary_role": self.employee_role.pk,
                "is_active": "false",
                "next": edit_url,
            },
        )

        self.assertRedirects(response, edit_url)
        target_user.refresh_from_db()
        self.assertFalse(target_user.is_active)

        response = self.client.post(
            edit_url,
            {
                "primary_role": self.employee_role.pk,
                "is_active": "true",
                "next": edit_url,
            },
        )

        self.assertRedirects(response, edit_url)
        target_user.refresh_from_db()
        self.assertTrue(target_user.is_active)
