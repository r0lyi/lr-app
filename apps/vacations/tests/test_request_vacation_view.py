"""Tests basicos de la vista para solicitar vacaciones."""

from django.urls import reverse

from apps.users.models import Role
from apps.vacations.models import VacationRequest

from .base import VacationBaseTestCase


class VacationRequestViewTests(VacationBaseTestCase):
    """Comprueba el formulario minimo de solicitud del empleado."""

    @classmethod
    def setUpTestData(cls):
        cls.rrhh_role = Role.objects.get(name="rrhh")

    def create_rrhh_user_with_employee_profile(self, *, email, dni):
        """Crea un usuario RRHH con ficha Employee para solicitar vacaciones."""

        user, employee = self.create_employee_user(email=email, dni=dni)
        user.roles.set([self.rrhh_role])
        return user, employee

    def test_employee_can_open_request_page(self):
        user, _employee = self.create_employee_user(
            email="employee-vacations@example.com",
            dni="12345678Z",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("vacations:create-request"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solicitar vacaciones")
        self.assertContains(response, "Derecho anual")
        self.assertContains(response, "selected-days-counter")
        self.assertContains(response, "Solicitud de periodo vacacional")
        self.assertContains(response, "Rango actual:")
        self.assertContains(response, "Informacion adicional")
        self.assertContains(response, "Confirmar")
        self.assertContains(response, "selected-range-summary")

    def test_rrhh_with_employee_profile_can_open_request_page(self):
        user, _employee = self.create_rrhh_user_with_employee_profile(
            email="rrhh-vacations@example.com",
            dni="22222222J",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("vacations:create-request"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solicitar vacaciones")
        self.assertContains(response, reverse("dashboard:rrhh-home"))
        self.assertContains(response, reverse("vacations:create-request"))

    def test_employee_can_create_pending_vacation_request(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-create@example.com",
            dni="00000000T",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("vacations:create-request"),
            {
                "start_date": "2026-07-01",
                "end_date": "2026-07-05",
                "employee_comment": "Vacaciones de verano",
            },
        )

        self.assertRedirects(response, reverse("vacations:create-request"))

        vacation_request = VacationRequest.objects.get(employee=employee)
        self.assertEqual(vacation_request.status.name, "pending")
        self.assertEqual(str(vacation_request.requested_days), "5.00")
        self.assertEqual(vacation_request.employee_comment, "Vacaciones de verano")

    def test_rrhh_with_employee_profile_can_create_pending_vacation_request(self):
        user, employee = self.create_rrhh_user_with_employee_profile(
            email="rrhh-vacations-create@example.com",
            dni="44444444A",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("vacations:create-request"),
            {
                "start_date": "2026-07-01",
                "end_date": "2026-07-05",
                "employee_comment": "Vacaciones RRHH",
            },
        )

        self.assertRedirects(response, reverse("vacations:create-request"))

        vacation_request = VacationRequest.objects.get(employee=employee)
        self.assertEqual(vacation_request.status.name, "pending")
        self.assertEqual(str(vacation_request.requested_days), "5.00")
        self.assertEqual(vacation_request.employee_comment, "Vacaciones RRHH")

    def test_invalid_post_keeps_form_and_shows_error(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-invalid@example.com",
            dni="11111111H",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("vacations:create-request"),
            {
                "start_date": "2026-07-10",
                "end_date": "2026-07-05",
                "employee_comment": "Necesito revisar estas fechas",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "La fecha de fin no puede ser anterior a la fecha de inicio.",
        )
        self.assertContains(response, 'value="2026-07-10"', html=False)
        self.assertContains(response, 'value="2026-07-05"', html=False)
        self.assertContains(response, "Necesito revisar estas fechas")
        self.assertEqual(VacationRequest.objects.filter(employee=employee).count(), 0)
