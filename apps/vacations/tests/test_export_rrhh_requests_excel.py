"""Tests del flujo de exportacion Excel desde el panel de RRHH."""

from datetime import date
from io import BytesIO
from zipfile import ZipFile

from django.urls import reverse
from django.utils import timezone

from apps.audit.models import ExportHistory
from apps.audit.services import EXPORT_TYPE_RRHH_VACATION_REQUESTS
from apps.users.models import Role, User
from apps.vacations.models import VacationRequest, VacationStatus

from .base import VacationBaseTestCase


class ExportRrhhRequestsExcelViewTests(VacationBaseTestCase):
    """Comprueba la descarga y el registro del historial de exportaciones."""

    @classmethod
    def setUpTestData(cls):
        cls.rrhh_role = Role.objects.get(name="rrhh")
        cls.admin_role = Role.objects.get(name="admin")
        cls.pending_status = VacationStatus.objects.get(name="pending")
        cls.approved_status = VacationStatus.objects.get(name="approved")

    def create_rrhh_user(self, *, email, dni):
        """Crea un usuario activo listo para operar como RRHH."""

        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        user.roles.set([self.rrhh_role])
        return user

    def create_admin_user(self, *, email, dni):
        """Crea un admin activo para exportar desde su panel."""

        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        user.roles.set([self.admin_role])
        return user

    def test_rrhh_can_export_filtered_requests_to_excel_and_log_history(self):
        rrhh_user = self.create_rrhh_user(
            email="rrhh-export@example.com",
            dni="77777777B",
        )
        _employee_one_user, employee_one = self.create_employee_user(
            email="employee-export-one@example.com",
            dni="88888888Y",
        )
        _employee_two_user, employee_two = self.create_employee_user(
            email="employee-export-two@example.com",
            dni="99999999R",
        )

        VacationRequest.objects.create(
            employee=employee_one,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )
        VacationRequest.objects.create(
            employee=employee_two,
            status=self.approved_status,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 3),
            requested_days="3.00",
        )

        self.client.force_login(rrhh_user)

        response = self.client.get(
            reverse("vacations:export-rrhh-requests-excel"),
            {"status": "pending"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("attachment;", response["Content-Disposition"])
        expected_file_name = f'vacation_{timezone.localdate().strftime("%d-%m-%Y")}.xlsx'
        self.assertIn(expected_file_name, response["Content-Disposition"])

        export_history = ExportHistory.objects.get()
        self.assertEqual(
            export_history.export_type,
            EXPORT_TYPE_RRHH_VACATION_REQUESTS,
        )
        self.assertEqual(export_history.status, "success")
        self.assertEqual(export_history.total_records, 1)
        self.assertEqual(export_history.filters_json["status"], "pending")
        self.assertEqual(export_history.file_name, expected_file_name)
        self.assertTrue(export_history.file_path)

        workbook = ZipFile(BytesIO(response.content))
        sheet_xml = workbook.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertIn("Lopez", sheet_xml)
        self.assertIn("Ana", sheet_xml)
        self.assertIn("pending", sheet_xml)
        self.assertNotIn("approved", sheet_xml)

    def test_admin_can_export_filtered_requests_to_excel_and_log_history(self):
        admin_user = self.create_admin_user(
            email="admin-export@example.com",
            dni="90909090A",
        )
        _employee_one_user, employee_one = self.create_employee_user(
            email="employee-admin-export-one@example.com",
            dni="23232323T",
        )
        _employee_two_user, employee_two = self.create_employee_user(
            email="employee-admin-export-two@example.com",
            dni="34343434H",
        )

        VacationRequest.objects.create(
            employee=employee_one,
            status=self.pending_status,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 4),
            requested_days="4.00",
        )
        VacationRequest.objects.create(
            employee=employee_two,
            status=self.approved_status,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 2),
            requested_days="2.00",
        )

        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("vacations:export-rrhh-requests-excel"),
            {"status": "pending"},
        )

        self.assertEqual(response.status_code, 200)
        export_history = ExportHistory.objects.get()
        self.assertEqual(export_history.user, admin_user)
        self.assertEqual(export_history.total_records, 1)
