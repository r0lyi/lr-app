"""Tests del borrado de usuarios desde Django Admin."""

from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.audit.models import AuditLog
from apps.audit.services import (
    AUDIT_ACTION_USER_CREATED,
    AUDIT_RESOURCE_TYPE_USER,
)
from apps.employees.models import Employee
from apps.notifications.models import Notification
from apps.users.models import User
from apps.vacations.models import (
    VacationRequest,
    VacationRequestHistory,
    VacationStatus,
)


class DjangoAdminUserDeleteTests(TestCase):
    """Cubre la cascada esperada al borrar usuarios desde /admin/."""

    def test_admin_can_delete_user_with_related_data(self):
        admin_user = User.objects.create_superuser(
            email="super-admin-delete@example.com",
            dni="34343434H",
            password="PruebaSegura123!",
        )
        target_user = User.objects.create_user(
            email="target-delete@example.com",
            dni="27272727V",
            password="PruebaSegura123!",
            is_active=True,
        )
        employee = Employee.objects.create(
            user=target_user,
            first_name="Ana",
            last_name="Delete",
            phone="600123123",
            hire_date=date(2024, 1, 15),
        )
        pending_status = VacationStatus.objects.get(name="pending")
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=pending_status,
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 12),
            requested_days=Decimal("3.00"),
        )
        VacationRequestHistory.objects.create(
            vacation_request=vacation_request,
            previous_status=None,
            new_status=pending_status,
            changed_by=target_user,
            comment="Creada para probar cascada.",
        )
        Notification.objects.create(
            user=target_user,
            created_by=admin_user,
            title="Prueba",
            message="Notificacion del usuario eliminado.",
        )
        AuditLog.objects.create(
            user=target_user,
            action=AUDIT_ACTION_USER_CREATED,
            resource_type=AUDIT_RESOURCE_TYPE_USER,
            resource_id=target_user.pk,
            description="Log ejecutado por el usuario eliminado.",
        )
        AuditLog.objects.create(
            user=admin_user,
            action=AUDIT_ACTION_USER_CREATED,
            resource_type=AUDIT_RESOURCE_TYPE_USER,
            resource_id=target_user.pk,
            description="Log sobre el usuario eliminado.",
        )
        retained_log = AuditLog.objects.create(
            user=admin_user,
            action=AUDIT_ACTION_USER_CREATED,
            resource_type=AUDIT_RESOURCE_TYPE_USER,
            resource_id=admin_user.pk,
            description="Log ajeno al usuario eliminado.",
        )

        self.client.force_login(admin_user)
        confirmation_response = self.client.get(
            reverse("admin:users_user_delete", args=[target_user.pk]),
        )
        self.assertEqual(
            confirmation_response.status_code,
            200,
            confirmation_response.content.decode()[:1000],
        )
        self.assertFalse(confirmation_response.context["perms_lacking"])
        self.assertFalse(confirmation_response.context["protected"])
        response = self.client.post(
            reverse("admin:users_user_delete", args=[target_user.pk]),
            {"post": "yes"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200, response.content.decode()[:1000])
        self.assertFalse(User.objects.filter(pk=target_user.pk).exists())
        self.assertFalse(Employee.objects.filter(pk=employee.pk).exists())
        self.assertFalse(VacationRequest.objects.filter(pk=vacation_request.pk).exists())
        self.assertFalse(
            VacationRequestHistory.objects.filter(
                vacation_request_id=vacation_request.pk,
            ).exists()
        )
        self.assertFalse(Notification.objects.filter(user_id=target_user.pk).exists())
        self.assertFalse(AuditLog.objects.filter(user_id=target_user.pk).exists())
        self.assertFalse(
            AuditLog.objects.filter(
                resource_type=AUDIT_RESOURCE_TYPE_USER,
                resource_id=target_user.pk,
            ).exists()
        )
        self.assertTrue(AuditLog.objects.filter(pk=retained_log.pk).exists())
