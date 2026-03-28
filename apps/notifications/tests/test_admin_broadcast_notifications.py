"""Tests de avisos generales enviados desde el panel de administracion."""

from django.test import TestCase
from django.urls import reverse

from apps.notifications.models import Notification
from apps.notifications.selectors import get_admin_broadcast_notification_recipients
from apps.notifications.services import create_admin_broadcast_notifications
from apps.users.models import Role, User


class AdminBroadcastNotificationsTests(TestCase):
    """Comprueba el envio general de notificaciones desde administracion."""

    @classmethod
    def setUpTestData(cls):
        cls.admin_role = Role.objects.get(name="admin")

    def create_active_user(self, *, email, dni):
        """Crea un usuario activo reutilizable en esta suite."""

        return User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )

    def test_service_creates_notifications_for_all_active_users(self):
        admin_user = self.create_active_user(
            email="admin-broadcast-service@example.com",
            dni="56565656P",
        )
        admin_user.roles.set([self.admin_role])

        employee_user = self.create_active_user(
            email="employee-broadcast-service@example.com",
            dni="78787878K",
        )
        inactive_user = self.create_active_user(
            email="inactive-broadcast-service@example.com",
            dni="90909090A",
        )
        inactive_user.is_active = False
        inactive_user.save(update_fields=["is_active"])

        notifications = create_admin_broadcast_notifications(
            sender=admin_user,
            title="Aviso general",
            message="Hoy se realizará una revisión del sistema.",
        )

        expected_count = get_admin_broadcast_notification_recipients().count()
        self.assertEqual(len(notifications), expected_count)
        self.assertEqual(
            Notification.objects.filter(
                notification_type=Notification.Type.ADMIN_BROADCAST_MESSAGE
            ).count(),
            expected_count,
        )
        recipients = set(
            Notification.objects.filter(
                notification_type=Notification.Type.ADMIN_BROADCAST_MESSAGE
            ).values_list("user__email", flat=True)
        )
        self.assertIn(admin_user.email, recipients)
        self.assertIn(employee_user.email, recipients)
        self.assertNotIn(inactive_user.email, recipients)

    def test_admin_can_send_broadcast_notification_from_admin_home(self):
        admin_user = self.create_active_user(
            email="admin-broadcast-view@example.com",
            dni="23232323T",
        )
        admin_user.roles.set([self.admin_role])

        employee_user = self.create_active_user(
            email="employee-broadcast-view@example.com",
            dni="45454545J",
        )

        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("dashboard:admin-home"),
            {
                "title": "Comunicado general",
                "message": "Mañana habrá una actualización prevista del sistema.",
            },
        )

        self.assertRedirects(response, reverse("dashboard:admin-home"))
        notifications = Notification.objects.filter(
            notification_type=Notification.Type.ADMIN_BROADCAST_MESSAGE
        ).order_by("user__email")
        expected_count = get_admin_broadcast_notification_recipients().count()
        self.assertEqual(notifications.count(), expected_count)
        self.assertEqual(
            notifications.filter(created_by=admin_user).count(),
            expected_count,
        )
        self.assertIn(admin_user.email, {item.user.email for item in notifications})
        self.assertIn(employee_user.email, {item.user.email for item in notifications})

    def test_invalid_broadcast_notification_keeps_errors_on_admin_home(self):
        admin_user = self.create_active_user(
            email="admin-broadcast-invalid@example.com",
            dni="67676767A",
        )
        admin_user.roles.set([self.admin_role])

        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("dashboard:admin-home"),
            {
                "title": "",
                "message": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asunto general")
        self.assertContains(response, "Mensaje general")
        self.assertContains(response, "Este campo es obligatorio.")
        self.assertEqual(
            Notification.objects.filter(
                notification_type=Notification.Type.ADMIN_BROADCAST_MESSAGE
            ).count(),
            0,
        )
