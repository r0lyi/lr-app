"""Tests de lectura para el inbox interno de notificaciones."""

from datetime import date

from django.test import TestCase

from apps.employees.models import Employee
from apps.notifications.models import Notification
from apps.notifications.selectors import (
    get_unread_notifications_count,
    get_user_inbox_notification_by_id,
    get_user_inbox_notifications,
)
from apps.users.models import User
from apps.vacations.models import VacationRequest, VacationStatus


class NotificationInboxSelectorsTests(TestCase):
    """Verifica las consultas base que usara el inbox del usuario."""

    @classmethod
    def setUpTestData(cls):
        cls.pending_status = VacationStatus.objects.get(name="pending")

    def create_active_user(self, *, email, dni):
        """Crea un usuario activo reutilizable para esta suite."""

        return User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )

    def create_vacation_request_for_user(self, user):
        """Genera una solicitud asociada a un empleado para dar contexto."""

        employee = Employee.objects.create(
            user=user,
            first_name="Ana",
            last_name="Lopez",
            phone="600123123",
            hire_date=date(2024, 1, 15),
        )
        return VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )

    def test_get_user_inbox_notifications_returns_only_user_items(self):
        user = self.create_active_user(
            email="notifications-owner@example.com",
            dni="12345678Z",
        )
        other_user = self.create_active_user(
            email="notifications-other@example.com",
            dni="00000000T",
        )
        vacation_request = self.create_vacation_request_for_user(user)

        owned_notification = Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_REQUEST_STATUS,
            vacation_request=vacation_request,
            message="Tu solicitud ha cambiado de estado.",
        )
        Notification.objects.create(
            user=other_user,
            notification_type=Notification.Type.VACATION_INFO,
            message="Mensaje de otro usuario.",
        )

        notifications = list(get_user_inbox_notifications(user))

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0], owned_notification)
        self.assertEqual(notifications[0].vacation_request, vacation_request)

    def test_get_user_inbox_notifications_can_filter_unread_and_limit(self):
        user = self.create_active_user(
            email="notifications-filter@example.com",
            dni="11111111H",
        )

        first_notification = Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_INFO,
            message="Primera notificacion",
            is_read=False,
        )
        Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_INFO,
            message="Segunda notificacion",
            is_read=True,
        )

        unread_notifications = list(
            get_user_inbox_notifications(user, is_read=False, limit=1)
        )

        self.assertEqual(len(unread_notifications), 1)
        self.assertEqual(unread_notifications[0], first_notification)

    def test_get_unread_notifications_count_returns_only_pending_items(self):
        user = self.create_active_user(
            email="notifications-count@example.com",
            dni="22222222J",
        )

        Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_INFO,
            message="No leida 1",
            is_read=False,
        )
        Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_INFO,
            message="No leida 2",
            is_read=False,
        )
        Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_INFO,
            message="Ya leida",
            is_read=True,
        )

        self.assertEqual(get_unread_notifications_count(user), 2)

    def test_get_user_inbox_notification_by_id_prevents_cross_user_access(self):
        user = self.create_active_user(
            email="notifications-detail@example.com",
            dni="33333333P",
        )
        other_user = self.create_active_user(
            email="notifications-detail-other@example.com",
            dni="44444444A",
        )

        own_notification = Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_INFO,
            message="Notificacion propia",
        )
        Notification.objects.create(
            user=other_user,
            notification_type=Notification.Type.VACATION_INFO,
            message="Notificacion ajena",
        )

        fetched_notification = get_user_inbox_notification_by_id(
            user,
            own_notification.pk,
        )

        self.assertEqual(fetched_notification, own_notification)
