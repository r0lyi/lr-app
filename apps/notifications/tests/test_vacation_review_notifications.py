"""Tests de notificaciones al empleado cuando RRHH cambia el estado."""

from datetime import date

from django.test import TestCase

from apps.employees.models import Employee
from apps.notifications.models import Notification
from apps.notifications.services import create_vacation_status_changed_notification
from apps.users.models import User
from apps.vacations.models import VacationRequest, VacationStatus


class VacationReviewNotificationsTests(TestCase):
    """Verifica la regla de notificar solo si cambia el estado."""

    @classmethod
    def setUpTestData(cls):
        cls.pending_status = VacationStatus.objects.get(name="pending")

    def create_active_user(self, *, email, dni):
        """Crea un usuario activo reutilizable en esta suite."""

        return User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )

    def create_employee_vacation_request(self):
        """Crea una solicitud base para probar notificaciones de revision."""

        employee_user = self.create_active_user(
            email="employee-review-notification@example.com",
            dni="12345678Z",
        )
        employee = Employee.objects.create(
            user=employee_user,
            first_name="Ana",
            last_name="Lopez",
            phone="600123123",
            hire_date=date(2024, 1, 15),
        )
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )
        return employee_user, vacation_request

    def test_employee_is_notified_when_status_changes(self):
        employee_user, vacation_request = self.create_employee_vacation_request()

        notification = create_vacation_status_changed_notification(
            vacation_request,
            previous_status_name="pending",
            new_status_name="approved",
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, employee_user)
        self.assertEqual(
            notification.notification_type,
            Notification.Type.VACATION_REQUEST_STATUS,
        )
        self.assertEqual(notification.previous_status_name, "pending")
        self.assertIn("pending -> approved", notification.message)

    def test_employee_is_not_notified_when_status_does_not_change(self):
        _employee_user, vacation_request = self.create_employee_vacation_request()

        notification = create_vacation_status_changed_notification(
            vacation_request,
            previous_status_name="pending",
            new_status_name="pending",
        )

        self.assertIsNone(notification)
        self.assertEqual(Notification.objects.count(), 0)
