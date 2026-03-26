"""Tests basicos de la vista para solicitar vacaciones."""

from django.urls import reverse

from apps.vacations.models import VacationRequest

from .base import VacationBaseTestCase


class VacationRequestViewTests(VacationBaseTestCase):
    """Comprueba el formulario minimo de solicitud del empleado."""

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
