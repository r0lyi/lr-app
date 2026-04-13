"""Tests basicos de la vista para solicitar vacaciones."""

from datetime import date, timedelta

from django.urls import reverse
from django.utils import timezone

from apps.notifications.models import Notification
from apps.users.models import Role, User
from apps.vacations.models import VacationRequest, VacationStatus

from .base import VacationBaseTestCase


class VacationRequestViewTests(VacationBaseTestCase):
    """Comprueba el formulario minimo de solicitud del empleado."""

    @classmethod
    def setUpTestData(cls):
        cls.rrhh_role = Role.objects.get(name="rrhh")
        cls.admin_role = Role.objects.get(name="admin")
        cls.pending_status = VacationStatus.objects.get(name="pending")
        cls.approved_status = VacationStatus.objects.get(name="approved")

    def get_request_range(self, *, offset_days=35, duration_days=5):
        """Devuelve un rango valido relativo a la fecha actual del sistema."""

        start_date = timezone.localdate() + timedelta(days=offset_days)
        end_date = start_date + timedelta(days=duration_days - 1)
        return start_date, end_date

    def post_vacation_request(
        self,
        *,
        start_date,
        end_date,
        employee_comment="",
    ):
        """Envuelve el POST del formulario para mantener los tests mas claros."""

        return self.client.post(
            reverse("vacations:create-request"),
            {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "employee_comment": employee_comment,
            },
        )

    def create_rrhh_user(self, *, email, dni):
        """Crea un usuario RRHH activo para las pruebas de integracion."""

        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        user.roles.set([self.rrhh_role])
        return user

    def create_rrhh_user_with_employee_profile(self, *, email, dni):
        """Crea un usuario RRHH con ficha Employee para solicitar vacaciones."""

        user, employee = self.create_employee_user(email=email, dni=dni)
        user.roles.set([self.rrhh_role])
        return user, employee

    def create_admin_user_with_employee_profile(self, *, email, dni):
        """Crea un admin con ficha Employee para probar el flujo real."""

        user, employee = self.create_employee_user(email=email, dni=dni)
        user.roles.set([self.admin_role])
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

    def test_admin_can_open_request_page_for_testing(self):
        user, _employee = self.create_admin_user_with_employee_profile(
            email="admin-vacations-open@example.com",
            dni="22222222J",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("vacations:create-request"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solicitar vacaciones")
        self.assertContains(response, "Derecho anual")
        self.assertContains(response, reverse("dashboard:admin-home"))

    def test_rrhh_with_employee_profile_can_open_request_page(self):
        user, _employee = self.create_rrhh_user_with_employee_profile(
            email="rrhh-vacations@example.com",
            dni="13579135G",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("vacations:create-request"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solicitar vacaciones")
        self.assertContains(response, "Derecho anual")
        self.assertContains(response, reverse("dashboard:rrhh-home"))
        self.assertContains(response, reverse("vacations:create-request"))

    def test_employee_can_create_pending_vacation_request(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-create@example.com",
            dni="00000000T",
        )
        rrhh_user = self.create_rrhh_user(
            email="rrhh-vacations-create@example.com",
            dni="77777777B",
        )

        self.client.force_login(user)
        start_date, end_date = self.get_request_range(offset_days=40, duration_days=5)

        response = self.post_vacation_request(
            start_date=start_date,
            end_date=end_date,
            employee_comment="Vacaciones de verano",
        )

        self.assertRedirects(response, reverse("vacations:create-request"))

        vacation_request = VacationRequest.objects.get(employee=employee)
        self.assertEqual(vacation_request.status.name, "pending")
        self.assertEqual(vacation_request.start_date, start_date)
        self.assertEqual(vacation_request.end_date, end_date)
        self.assertEqual(str(vacation_request.requested_days), "5.00")
        self.assertEqual(vacation_request.employee_comment, "Vacaciones de verano")

        notification = Notification.objects.get(user=rrhh_user)
        self.assertEqual(
            notification.notification_type,
            Notification.Type.VACATION_REQUEST_SUBMISSION,
        )
        self.assertEqual(notification.vacation_request, vacation_request)
        self.assertIn("Ana Lopez", notification.message)

    def test_admin_can_create_pending_vacation_request_for_testing(self):
        user, employee = self.create_admin_user_with_employee_profile(
            email="admin-vacations-create@example.com",
            dni="33333333P",
        )
        rrhh_user = self.create_rrhh_user(
            email="rrhh-vacations-admin-create@example.com",
            dni="44444444A",
        )

        self.client.force_login(user)
        start_date, end_date = self.get_request_range(offset_days=45, duration_days=4)

        response = self.post_vacation_request(
            start_date=start_date,
            end_date=end_date,
            employee_comment="Prueba interna del panel admin",
        )

        self.assertRedirects(response, reverse("vacations:create-request"))

        vacation_request = VacationRequest.objects.get(employee=employee)
        self.assertEqual(vacation_request.status.name, "pending")
        self.assertEqual(str(vacation_request.requested_days), "4.00")
        self.assertEqual(
            vacation_request.employee_comment,
            "Prueba interna del panel admin",
        )

        notification = Notification.objects.get(user=rrhh_user)
        self.assertEqual(
            notification.notification_type,
            Notification.Type.VACATION_REQUEST_SUBMISSION,
        )
        self.assertEqual(notification.vacation_request, vacation_request)

    def test_rrhh_with_employee_profile_can_create_pending_vacation_request(self):
        user, employee = self.create_rrhh_user_with_employee_profile(
            email="rrhh-vacations-create@example.com",
            dni="44444444A",
        )
        reviewer_rrhh_user = self.create_rrhh_user(
            email="rrhh-vacations-reviewer@example.com",
            dni="13579135G",
        )

        self.client.force_login(user)
        start_date, end_date = self.get_request_range(offset_days=50, duration_days=5)

        response = self.post_vacation_request(
            start_date=start_date,
            end_date=end_date,
            employee_comment="Vacaciones RRHH",
        )

        self.assertRedirects(response, reverse("vacations:create-request"))

        vacation_request = VacationRequest.objects.get(employee=employee)
        self.assertEqual(vacation_request.status.name, "pending")
        self.assertEqual(vacation_request.start_date, start_date)
        self.assertEqual(vacation_request.end_date, end_date)
        self.assertEqual(str(vacation_request.requested_days), "5.00")
        self.assertEqual(vacation_request.employee_comment, "Vacaciones RRHH")

        notification = Notification.objects.get(user=reviewer_rrhh_user)
        self.assertEqual(
            notification.notification_type,
            Notification.Type.VACATION_REQUEST_SUBMISSION,
        )
        self.assertEqual(notification.vacation_request, vacation_request)

    def test_invalid_post_keeps_form_and_shows_error(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-invalid@example.com",
            dni="11111111H",
        )

        self.client.force_login(user)

        response = self.post_vacation_request(
            start_date=date(2026, 7, 10),
            end_date=date(2026, 7, 5),
            employee_comment="Necesito revisar estas fechas",
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

    def test_request_rejects_period_shorter_than_three_days(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-short@example.com",
            dni="12121212M",
        )

        self.client.force_login(user)
        start_date, end_date = self.get_request_range(offset_days=40, duration_days=2)

        response = self.post_vacation_request(
            start_date=start_date,
            end_date=end_date,
            employee_comment="Solo necesito dos dias",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "La solicitud debe incluir entre 3 y 30 dias naturales.",
        )
        self.assertEqual(VacationRequest.objects.filter(employee=employee).count(), 0)

    def test_request_rejects_period_longer_than_thirty_days(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-long@example.com",
            dni="34343434H",
        )

        self.client.force_login(user)
        start_date, end_date = self.get_request_range(offset_days=40, duration_days=31)

        response = self.post_vacation_request(
            start_date=start_date,
            end_date=end_date,
            employee_comment="Intento de vacaciones demasiado largas",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "La solicitud debe incluir entre 3 y 30 dias naturales.",
        )
        self.assertEqual(VacationRequest.objects.filter(employee=employee).count(), 0)

    def test_request_rejects_days_above_employee_annual_entitlement(self):
        request_year = timezone.localdate().year + 1
        user, employee = self.create_employee_user(
            email="employee-vacations-entitlement@example.com",
            dni="56565656P",
            hire_date=date(request_year, 11, 15),
        )

        self.client.force_login(user)

        response = self.post_vacation_request(
            start_date=date(request_year, 12, 20),
            end_date=date(request_year, 12, 24),
            employee_comment="Quiero cinco dias aunque mi alta es reciente",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"Los dias solicitados superan el derecho anual disponible para {request_year}.",
        )
        self.assertEqual(VacationRequest.objects.filter(employee=employee).count(), 0)

    def test_request_rejects_start_date_in_the_past(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-past@example.com",
            dni="78787878K",
        )

        self.client.force_login(user)
        today = timezone.localdate()

        response = self.post_vacation_request(
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=2),
            employee_comment="Fechas atrasadas",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "La fecha de inicio no puede estar en el pasado.",
        )
        self.assertEqual(VacationRequest.objects.filter(employee=employee).count(), 0)

    def test_request_rejects_start_date_without_minimum_notice(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-notice@example.com",
            dni="90909090A",
        )

        self.client.force_login(user)
        start_date, end_date = self.get_request_range(offset_days=20, duration_days=5)

        response = self.post_vacation_request(
            start_date=start_date,
            end_date=end_date,
            employee_comment="No cumplo el preaviso",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "La fecha de inicio debe solicitarse con al menos 30 dias naturales de antelacion.",
        )
        self.assertEqual(VacationRequest.objects.filter(employee=employee).count(), 0)

    def test_request_rejects_when_another_pending_request_is_open(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-open-request@example.com",
            dni="91919191J",
        )
        existing_start, existing_end = self.get_request_range(
            offset_days=40,
            duration_days=5,
        )
        VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=existing_start,
            end_date=existing_end,
            requested_days="5.00",
        )

        self.client.force_login(user)
        start_date, end_date = self.get_request_range(offset_days=60, duration_days=5)

        response = self.post_vacation_request(
            start_date=start_date,
            end_date=end_date,
            employee_comment="Segunda solicitud pendiente",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Ya existe una solicitud pendiente. Debe resolverse antes de registrar una nueva.",
        )
        self.assertEqual(VacationRequest.objects.filter(employee=employee).count(), 1)

    def test_request_rejects_when_dates_overlap_existing_approved_request(self):
        user, employee = self.create_employee_user(
            email="employee-vacations-overlap@example.com",
            dni="92929292T",
        )
        existing_start, existing_end = self.get_request_range(
            offset_days=50,
            duration_days=5,
        )
        VacationRequest.objects.create(
            employee=employee,
            status=self.approved_status,
            start_date=existing_start,
            end_date=existing_end,
            requested_days="5.00",
        )

        self.client.force_login(user)

        response = self.post_vacation_request(
            start_date=existing_start + timedelta(days=2),
            end_date=existing_end + timedelta(days=2),
            employee_comment="Se solapa con una aprobada",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Ya existe una solicitud pendiente o aprobada que se solapa con ese periodo.",
        )
        self.assertEqual(VacationRequest.objects.filter(employee=employee).count(), 1)
