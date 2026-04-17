"""Tests del historial de auditoria mostrado al administrador."""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.audit.services import (
    AUDIT_ACTION_USER_ACCESS_STATE_CHANGED,
    AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED,
    AUDIT_RESOURCE_TYPE_USER,
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
        self.assertContains(response, "Historial de Actividad")
        self.assertContains(response, "Buscar actividad")
        self.assertContains(response, "Tipo de cambio")
        self.assertContains(response, "Realizado por")
        self.assertContains(response, "Qué sucedió")
        self.assertContains(response, "Acciones")
        self.assertContains(response, "Total Actividades")
        self.assertContains(response, "Cambios de Rol")
        self.assertContains(response, "Cambios de Acceso")
        self.assertNotContains(response, "Cambios de Departamento")
        self.assertNotContains(response, "Cambio de departamento")
        self.assertContains(
            response,
            reverse("dashboard:admin-user-edit", args=[admin_user.pk]),
        )
        self.assertContains(
            response,
            "admin-audit-view@example.com cambió el rol principal de empleado@example.com de Empleado a RRHH.",
        )

    def test_admin_can_filter_audit_log_by_text_action_and_date_range(self):
        admin_user = self.create_active_user(
            email="admin-audit-filter@example.com",
            dni="15151515N",
        )
        admin_user.roles.set([self.admin_role])

        target_user = self.create_active_user(
            email="target-audit-filter@example.com",
            dni="26262626F",
        )
        target_user.roles.set([self.employee_role])

        role_log = AuditLog.objects.create(
            user=admin_user,
            action=AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED,
            resource_type=AUDIT_RESOURCE_TYPE_USER,
            resource_id=target_user.pk,
            description=(
                "admin-audit-filter@example.com cambió el rol principal de "
                "target-audit-filter@example.com de Empleado a RRHH."
            ),
        )
        access_log = AuditLog.objects.create(
            user=admin_user,
            action=AUDIT_ACTION_USER_ACCESS_STATE_CHANGED,
            resource_type=AUDIT_RESOURCE_TYPE_USER,
            resource_id=target_user.pk,
            description=(
                "admin-audit-filter@example.com desactivó el acceso al sistema "
                "de target-audit-filter@example.com."
            ),
        )

        now = timezone.now()
        AuditLog.objects.filter(pk=role_log.pk).update(created_at=now - timedelta(days=5))
        AuditLog.objects.filter(pk=access_log.pk).update(
            created_at=now - timedelta(days=1)
        )

        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("audit:activity-log"),
            {
                "search": "acceso",
                "action": AUDIT_ACTION_USER_ACCESS_STATE_CHANGED,
                "start_date": (now - timedelta(days=2)).date().isoformat(),
                "end_date": now.date().isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cambio de acceso")
        self.assertContains(response, "desactivó el acceso")
        self.assertNotContains(response, "de Empleado a RRHH")
        self.assertEqual(response.context["audit_logs_count"], 1)
        self.assertEqual(response.context["visible_access_changes"], 1)
        self.assertEqual(response.context["visible_role_changes"], 0)

    def test_admin_activity_log_is_paginated_by_ten(self):
        admin_user = self.create_active_user(
            email="admin-audit-pagination@example.com",
            dni=self.build_valid_dni(33000000),
        )
        admin_user.roles.set([self.admin_role])
        for index in range(12):
            AuditLog.objects.create(
                user=admin_user,
                action=AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED,
                resource_type=AUDIT_RESOURCE_TYPE_USER,
                resource_id=admin_user.pk,
                description=f"Actividad paginada {index:02d}",
            )

        self.client.force_login(admin_user)

        first_page = self.client.get(reverse("audit:activity-log"))
        second_page = self.client.get(reverse("audit:activity-log"), {"page": "2"})

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(first_page.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(first_page.context["audit_logs_count"], 12)
        self.assertEqual(len(first_page.context["audit_logs"]), 10)
        self.assertContains(first_page, "Mostrando 1-10 de 12 actividades")

        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(second_page.context["audit_logs"]), 2)
        self.assertContains(second_page, "Mostrando 11-12 de 12 actividades")
