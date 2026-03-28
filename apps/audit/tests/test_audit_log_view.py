"""Tests del historial de auditoria mostrado al administrador."""

from django.urls import reverse

from apps.audit.models import AuditLog
from apps.audit.services import (
    AUDIT_ACTION_USER_DEPARTMENT_CHANGED,
    AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED,
    AUDIT_RESOURCE_TYPE_USER,
    build_user_department_change_description,
    build_user_role_change_description,
)
from apps.dashboard.tests.base import DashboardRoleBaseTestCase


class AuditLogViewTests(DashboardRoleBaseTestCase):
    """Verifica la lectura y el registro de actividad administrativa."""

    def test_admin_role_change_creates_a_clear_audit_log_entry(self):
        admin_user = self.create_active_user(
            email="admin-audit@example.com",
            dni="56565656P",
        )
        admin_user.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="target-audit@example.com",
            dni="23232323T",
        )
        target_user.roles.set([self.employee_role])

        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("dashboard:admin-user-primary-role", args=[target_user.pk]),
            {"primary_role": self.rrhh_role.pk},
        )

        self.assertRedirects(response, reverse("dashboard:admin-users"))
        audit_entry = AuditLog.objects.get(
            action=AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED,
            resource_type=AUDIT_RESOURCE_TYPE_USER,
            resource_id=target_user.pk,
        )
        self.assertEqual(audit_entry.user, admin_user)
        self.assertEqual(
            audit_entry.description,
            build_user_role_change_description(
                acting_user=admin_user,
                target_user=target_user,
                previous_role_name="employee",
                new_role_name="rrhh",
            ),
        )
        self.assertIn("cambió el rol principal", audit_entry.description)
        self.assertIn("de Empleado a RRHH", audit_entry.description)

    def test_admin_can_open_audit_log_view(self):
        admin_user = self.create_active_user(
            email="admin-audit-view@example.com",
            dni="78787878K",
        )
        admin_user.roles.set([self.admin_role])

        AuditLog.objects.create(
            user=admin_user,
            action=AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED,
            resource_type=AUDIT_RESOURCE_TYPE_USER,
            resource_id=admin_user.pk,
            description=(
                "admin-audit-view@example.com cambió el rol principal de "
                "empleado@example.com de Empleado a RRHH."
            ),
        )

        self.client.force_login(admin_user)

        response = self.client.get(reverse("audit:activity-log"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Actividad reciente")
        self.assertContains(response, "Realizado por")
        self.assertContains(response, "Detalle")
        self.assertContains(
            response,
            "admin-audit-view@example.com cambió el rol principal de empleado@example.com de Empleado a RRHH.",
        )

    def test_admin_department_change_creates_a_clear_audit_log_entry(self):
        admin_user = self.create_active_user(
            email="admin-audit-department@example.com",
            dni="45454545J",
        )
        admin_user.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="target-audit-department@example.com",
            dni="67676767A",
        )
        employee_profile = self.create_employee_profile(target_user)
        previous_department = self.create_department(name="Limpieza")
        new_department = self.create_department(name="Mantenimiento")
        employee_profile.department = previous_department
        employee_profile.save(update_fields=["department"])

        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("dashboard:admin-user-department", args=[target_user.pk]),
            {
                "department": new_department.pk,
                "next": reverse("dashboard:admin-user-edit", args=[target_user.pk]),
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:admin-user-edit", args=[target_user.pk]),
        )
        audit_entry = AuditLog.objects.get(
            action=AUDIT_ACTION_USER_DEPARTMENT_CHANGED,
            resource_type=AUDIT_RESOURCE_TYPE_USER,
            resource_id=target_user.pk,
        )
        self.assertEqual(audit_entry.user, admin_user)
        self.assertEqual(
            audit_entry.description,
            build_user_department_change_description(
                acting_user=admin_user,
                target_user=target_user,
                previous_department_name="Limpieza",
                new_department_name="Mantenimiento",
            ),
        )
        self.assertIn("cambió el departamento", audit_entry.description)
        self.assertIn("de Limpieza a Mantenimiento", audit_entry.description)
