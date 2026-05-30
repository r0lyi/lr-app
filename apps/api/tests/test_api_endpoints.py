"""Tests de contrato basico para la API JWT interna."""

from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.employees.models import Department, Employee
from apps.users.models import Role, User
from apps.vacations.models import VacationRequest, VacationStatus


class InternalApiEndpointTests(TestCase):
    """Valida autenticacion JWT, permisos y estructura JSON principal."""

    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="TI")
        cls.pending_status = VacationStatus.objects.get(name="pending")
        cls.approved_status = VacationStatus.objects.get(name="approved")
        cls.rejected_status = VacationStatus.objects.get(name="rejected")

        cls.admin = User.objects.create_user(
            email="admin@example.com",
            dni="00000000T",
            password="PruebaSegura123!",
            is_active=True,
        )
        cls.admin.roles.add(Role.objects.get(name="admin"))

        cls.employee_user = User.objects.create_user(
            email="empleado@example.com",
            dni="11111111H",
            password="PruebaSegura123!",
            is_active=True,
        )
        cls.employee = Employee.objects.create(
            user=cls.employee_user,
            department=cls.department,
            first_name="Roly",
            last_name="Silvestre",
            phone="600123123",
            hire_date=date(timezone.localdate().year - 1, 1, 1),
        )

        today = timezone.localdate()
        VacationRequest.objects.create(
            employee=cls.employee,
            status=cls.approved_status,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=1),
            requested_days="3.00",
        )
        VacationRequest.objects.create(
            employee=cls.employee,
            status=cls.pending_status,
            start_date=date(today.year, 8, 1),
            end_date=date(today.year, 8, 5),
            requested_days="5.00",
        )
        VacationRequest.objects.create(
            employee=cls.employee,
            status=cls.rejected_status,
            start_date=date(today.year, 9, 1),
            end_date=date(today.year, 9, 3),
            requested_days="3.00",
        )

    def setUp(self):
        self.client = APIClient()

    def authenticate_as(self, user):
        response = self.client.post(
            reverse("api-auth:token-obtain-pair"),
            {"dni": user.dni, "password": "PruebaSegura123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )

    def test_token_endpoint_accepts_dni_and_password(self):
        response = self.client.post(
            reverse("api-auth:token-obtain-pair"),
            {"dni": "00000000T", "password": "PruebaSegura123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_admin_can_generate_jwt_from_active_session(self):
        self.client.force_login(self.admin)

        response = self.client.post(reverse("api-auth:session-token"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )
        kpi_response = self.client.get(reverse("api:request-kpis"))
        self.assertEqual(kpi_response.status_code, 200)

    def test_employee_cannot_generate_session_jwt(self):
        self.client.force_login(self.employee_user)

        response = self.client.post(reverse("api-auth:session-token"))

        self.assertEqual(response.status_code, 403)

    def test_request_kpis_are_available_for_admin(self):
        self.authenticate_as(self.admin)

        response = self.client.get(reverse("api:request-kpis"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_solicitudes"], 3)
        self.assertEqual(response.data["solicitudes_pendientes"], 1)
        self.assertEqual(response.data["solicitudes_aprobadas"], 1)
        self.assertEqual(response.data["solicitudes_rechazadas"], 1)
        self.assertEqual(
            response.data["departamentos_con_mas_solicitudes"][0]["nombre"],
            "TI",
        )

    def test_user_kpis_are_available_for_admin(self):
        self.authenticate_as(self.admin)

        response = self.client.get(reverse("api:user-kpis"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_usuarios"], User.objects.count())
        self.assertEqual(
            response.data["usuarios_activos"],
            User.objects.filter(is_active=True).count(),
        )
        self.assertEqual(response.data["usuarios_en_vacaciones"], 1)
        self.assertEqual(
            response.data["perfiles_empleado_totales"],
            Employee.objects.count(),
        )
        self.assertEqual(
            response.data["usuarios_sin_perfil_empleado"],
            User.objects.filter(employee_profile__isnull=True).count(),
        )

    def test_employee_cannot_read_platform_kpis(self):
        self.authenticate_as(self.employee_user)

        response = self.client.get(reverse("api:user-kpis"))

        self.assertEqual(response.status_code, 403)

    def test_user_can_read_own_summary(self):
        self.authenticate_as(self.employee_user)

        response = self.client.get(
            reverse("api:user-summary", args=[self.employee_user.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "empleado@example.com")
        self.assertEqual(response.data["empleado"]["nombre_completo"], "Roly Silvestre")
        self.assertEqual(response.data["solicitudes"]["total"], 3)
        self.assertEqual(response.data["dias_vacaciones"]["reservados"], "8.00")
