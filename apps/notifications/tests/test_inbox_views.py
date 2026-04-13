"""Tests de acciones basicas sobre el inbox interno."""

from django.test import TestCase
from django.urls import reverse

from apps.notifications.models import Notification
from apps.users.models import User


class NotificationInboxViewsTests(TestCase):
    """Verifica marcar una o todas las notificaciones como leidas."""

    def create_active_user(self, *, email, dni):
        """Crea un usuario activo reutilizable para esta suite."""

        return User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )

    def test_user_can_mark_single_notification_as_read(self):
        user = self.create_active_user(
            email="notifications-read-one@example.com",
            dni="12345678Z",
        )
        notification = Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_INFO,
            message="Notificacion individual",
            is_read=False,
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("notifications:mark-read", args=[notification.pk]),
            {"next": reverse("dashboard:home")},
        )

        self.assertRedirects(
            response,
            reverse("dashboard:home"),
            fetch_redirect_response=False,
        )
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_user_can_mark_all_notifications_as_read(self):
        user = self.create_active_user(
            email="notifications-read-all@example.com",
            dni="00000000T",
        )
        Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_INFO,
            message="Notificacion uno",
            is_read=False,
        )
        Notification.objects.create(
            user=user,
            notification_type=Notification.Type.VACATION_INFO,
            message="Notificacion dos",
            is_read=False,
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("notifications:mark-all-read"),
            {"next": reverse("dashboard:home")},
        )

        self.assertRedirects(
            response,
            reverse("dashboard:home"),
            fetch_redirect_response=False,
        )
        self.assertEqual(
            Notification.objects.filter(user=user, is_read=False).count(),
            0,
        )
