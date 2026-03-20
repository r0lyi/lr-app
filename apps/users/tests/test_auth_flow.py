#uv run manage.py test apps.users.tests.test_auth_flow


from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.users.models import User


@override_settings(
    EMAIL_PROVIDER="console",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="test@example.com",
    FRONTEND_URL="http://testserver",
)
class AuthFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            email="empleado@example.com",
            dni="12345678Z",
        )

    def test_complete_auth_flow(self):
        response = self.client.post(
            reverse("auth:request-activation"),
            {"dni": "12345678Z"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        self.user.refresh_from_db()
        token = self.user.activation_token
        self.assertTrue(token)

        response = self.client.post(
            reverse("auth:set-password", args=[token]),
            {
                "password1": "PruebaSegura123!",
                "password2": "PruebaSegura123!",
            },
        )
        self.assertRedirects(response, reverse("auth:login"))

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.activation_token)

        response = self.client.post(
            reverse("auth:login"),
            {
                "dni": "12345678Z",
                "password": "PruebaSegura123!",
            },
        )
        self.assertRedirects(response, reverse("dashboard:home"))
