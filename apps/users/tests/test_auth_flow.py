"""Tests del flujo feliz de activacion, login y primer acceso autenticado."""


from datetime import timedelta

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.users.models import User


@override_settings(
    EMAIL_PROVIDER="console",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="test@example.com",
    FRONTEND_URL="http://testserver",
)
class AuthFlowTests(TestCase):
    """Valida el acceso inicial de un empleado sin ficha interna creada."""

    def setUp(self):
        """Crea un usuario precargado que aun no ha activado su acceso."""
        cache.clear()
        self.user = User.objects.create_user(
            email="empleado@example.com",
            dni="12345678Z",
        )

    def test_complete_auth_flow(self):
        """Comprueba que el login inicial continua hacia onboarding."""
        response = self.client.post(
            reverse("auth:request-activation"),
            {"dni": "12345678Z"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertContains(
            response,
            "Si el DNI corresponde a una cuenta, te hemos enviado un correo con las instrucciones para crear o recuperar tu contraseña.",
        )

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
            follow=True,
        )
        self.assertRedirects(response, reverse("employees:onboarding"))
        self.assertEqual(
            response.redirect_chain,
            [
                (reverse("dashboard:home"), 302),
                (reverse("employees:onboarding"), 302),
            ],
        )

    def test_login_requires_uppercase_dni_letter(self):
        """Rechaza el acceso cuando la letra del DNI se escribe en minusculas."""

        self.user.set_password("PruebaSegura123!")
        self.user.is_active = True
        self.user.save(update_fields=["password", "is_active"])

        response = self.client.post(
            reverse("auth:login"),
            {
                "dni": "12345678z",
                "password": "PruebaSegura123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "La letra del DNI debe escribirse en mayúsculas.",
        )

    def test_request_activation_htmx_updates_panel_with_confirmation_notice(self):
        """El submit HTMX debe actualizar el panel y mostrar el aviso persistente."""

        response = self.client.post(
            reverse("auth:request-activation"),
            {"dni": "12345678Z"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="request-activation-panel"', html=False)
        self.assertContains(response, 'hx-swap-oob="outerHTML"', html=False)
        self.assertContains(response, "Revisa tu correo")

    def test_public_auth_pages_include_language_switcher(self):
        """Las pantallas publicas del flujo auth deben permitir cambiar idioma."""

        self.user.activation_token = "token-valido"
        self.user.token_expires_at = timezone.now() + timedelta(hours=24)
        self.user.save(update_fields=["activation_token", "token_expires_at"])

        urls = (
            reverse("auth:login"),
            reverse("auth:request-activation"),
            reverse("auth:set-password", args=[self.user.activation_token]),
            reverse("auth:set-password", args=["token-invalido"]),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Cambiar idioma")
