"""Tests del aviso interno a RRHH cuando un empleado envia una solicitud."""

from datetime import date

from django.test import TestCase

from apps.employees.models import Employee
from apps.notifications.models import Notification
from apps.notifications.services import create_vacation_submission_notifications
from apps.users.models import Role, User
from apps.vacations.models import VacationRequest, VacationStatus


class VacationSubmissionNotificationsTests(TestCase):
    """Verifica la creacion de notificaciones de envio para RRHH."""

    @classmethod
    def setUpTestData(cls):
        cls.rrhh_role = Role.objects.get(name="rrhh")
        cls.pending_status = VacationStatus.objects.get(name="pending")

    def create_active_user(self, *, email, dni):
        """Crea un usuario activo reutilizable en esta suite."""

        return User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )

    def test_submission_notification_is_created_for_each_active_rrhh_user(self):
        rrhh_one = self.create_active_user(
            email="rrhh-one@example.com",
            dni="77777777B",
        )
        rrhh_one.roles.set([self.rrhh_role])

        rrhh_two = self.create_active_user(
            email="rrhh-two@example.com",
            dni="88888888Y",
        )
        rrhh_two.roles.set([self.rrhh_role])

        employee_user = self.create_active_user(
            email="employee-submit@example.com",
            dni="99999999R",
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

        create_vacation_submission_notifications(vacation_request)

        notifications = Notification.objects.order_by("user__email")
        self.assertEqual(notifications.count(), 2)
        self.assertEqual(
            list(notifications.values_list("user__email", flat=True)),
            ["rrhh-one@example.com", "rrhh-two@example.com"],
        )
        self.assertTrue(
            all(
                item.notification_type
                == Notification.Type.VACATION_REQUEST_SUBMISSION
                for item in notifications
            )
        )
        self.assertTrue(
            all(item.vacation_request == vacation_request for item in notifications)
        )
        self.assertIn("Ana Lopez", notifications.first().message)
        self.assertIn("01-07-2026", notifications.first().message)

