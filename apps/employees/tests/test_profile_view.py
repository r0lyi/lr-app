"""Tests de la vista basica de perfil del dominio employees."""

from django.contrib.auth import SESSION_KEY
from django.test import TestCase
from django.urls import reverse

from apps.employees.models import Employee
from apps.users.models import Role, User


class EmployeeProfileViewTests(TestCase):
    """Comprueba el acceso y el contenido minimo del perfil."""

    @classmethod
    def setUpTestData(cls):
        cls.admin_role = Role.objects.get(name="admin")

    def create_user_with_profile(self, *, email, dni):
        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        profile = Employee.objects.create(
            user=user,
            first_name="Ana",
            last_name="Lopez",
            phone="600123123",
            hire_date="2024-01-15",
            available_days=30,
            taken_days=5,
        )
        return user, profile

    def test_employee_profile_view_shows_employee_information(self):
        user, _profile = self.create_user_with_profile(
            email="employee-profile@example.com",
            dni="12345678Z",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("employees:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Perfil")
        self.assertContains(response, "¿Necesitas actualizar tus datos?")
        self.assertContains(response, "Ana")
        self.assertContains(response, "Lopez")
        self.assertContains(response, "employee-profile@example.com")
        self.assertContains(response, "600123123")
        self.assertContains(response, "2024-01-15")
        self.assertContains(response, "30")
        self.assertContains(response, "5")
        self.assertContains(response, "Editar datos del empleado")
        self.assertContains(response, "Guardar cambios")
        self.assertContains(response, "Cambiar contrasena")
        self.assertContains(response, "Actualizar contrasena")
        self.assertContains(response, "Departamento")
        self.assertContains(response, "Próximos pasos")
        self.assertNotContains(response, 'name="hire_date"')
        self.assertNotContains(response, 'name="email"')
        self.assertNotContains(response, 'name="department"')
        self.assertNotContains(response, 'name="available_days"')
        self.assertNotContains(response, 'name="taken_days"')

    def test_profile_view_edit_mode_keeps_save_actions_visible(self):
        user, _profile = self.create_user_with_profile(
            email="employee-profile-edit@example.com",
            dni="12345678Z",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("employees:profile") + "?edit=1")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guardar cambios")
        self.assertContains(response, "Cambiar contrasena")

    def test_admin_without_employee_profile_sees_clear_message(self):
        user = User.objects.create_user(
            email="admin-profile@example.com",
            dni="22222222J",
            password="PruebaSegura123!",
            is_active=True,
        )
        user.roles.set([self.admin_role])

        self.client.force_login(user)

        response = self.client.get(reverse("employees:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "No existe una ficha de empleado asociada a este usuario.",
        )
        self.assertContains(response, "admin-profile@example.com")
        self.assertContains(response, "Administrador")

    def test_profile_view_can_change_password(self):
        user, _profile = self.create_user_with_profile(
            email="employee-password@example.com",
            dni="00000000T",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("employees:profile"),
            {
                "old_password": "PruebaSegura123!",
                "new_password1": "NuevaClaveSegura123!",
                "new_password2": "NuevaClaveSegura123!",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("employees:profile"))
        user.refresh_from_db()
        self.assertTrue(user.check_password("NuevaClaveSegura123!"))
        self.assertEqual(str(self.client.session.get(SESSION_KEY)), str(user.pk))
        self.assertContains(
            response,
            "Tu contrasena se ha actualizado correctamente.",
        )

    def test_profile_view_can_update_employee_data(self):
        user, profile = self.create_user_with_profile(
            email="employee-update@example.com",
            dni="87654321X",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("employees:profile"),
            {
                "profile_action": "employee-update",
                "first_name": "Beatriz",
                "last_name": "Garcia",
                "phone": "699888777",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("employees:profile"))
        profile.refresh_from_db()
        self.assertEqual(profile.first_name, "Beatriz")
        self.assertEqual(profile.last_name, "Garcia")
        self.assertEqual(profile.phone, "699888777")
        self.assertIsNone(profile.department)
        self.assertEqual(profile.available_days, 30)
        self.assertEqual(profile.taken_days, 5)
        self.assertEqual(str(profile.hire_date), "2024-01-15")
        self.assertContains(
            response,
            "Tus datos de empleado se han actualizado correctamente.",
        )

    def test_profile_view_keeps_employee_form_when_update_is_invalid(self):
        user, profile = self.create_user_with_profile(
            email="employee-update-invalid@example.com",
            dni="12345678Z",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("employees:profile"),
            {
                "profile_action": "employee-update",
                "first_name": "",
                "last_name": "Lopez",
                "phone": "600123123",
            },
        )

        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(profile.first_name, "Ana")
        self.assertIn("first_name", response.context["employee_form"].errors)

    def test_profile_view_keeps_form_when_password_change_is_invalid(self):
        user, _profile = self.create_user_with_profile(
            email="employee-password-invalid@example.com",
            dni="13579135G",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("employees:profile"),
            {
                "old_password": "ClaveIncorrecta123!",
                "new_password1": "NuevaClaveSegura123!",
                "new_password2": "NuevaClaveSegura123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password("PruebaSegura123!"))
        self.assertIn("old_password", response.context["password_form"].errors)
