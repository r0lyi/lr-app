"""Tests del flujo de exportacion Excel desde el panel de RRHH."""

import re
from datetime import date
from io import BytesIO
from xml.etree import ElementTree
from zipfile import ZipFile

from django.core import mail
from django.urls import reverse
from django.utils import timezone

from apps.audit.models import ExportHistory
from apps.audit.services import EXPORT_TYPE_RRHH_VACATION_REQUESTS
from apps.users.models import Role, User
from apps.vacations.models import VacationRequest, VacationStatus

from .base import VacationBaseTestCase


XLSX_NAMESPACE = {"sheet": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _read_workbook_file(file_content, path):
    with ZipFile(BytesIO(file_content)) as workbook:
        return workbook.read(path).decode("utf-8")


def _read_sheet_rows(file_content):
    sheet_xml = _read_workbook_file(file_content, "xl/worksheets/sheet1.xml")
    root = ElementTree.fromstring(sheet_xml)

    rows = []
    for row in root.findall(".//sheet:row", XLSX_NAMESPACE):
        values = []
        for cell in row.findall("sheet:c", XLSX_NAMESPACE):
            inline_text = cell.find("sheet:is/sheet:t", XLSX_NAMESPACE)
            numeric_value = cell.find("sheet:v", XLSX_NAMESPACE)
            if inline_text is not None:
                values.append(inline_text.text or "")
            elif numeric_value is not None:
                values.append(numeric_value.text or "")
            else:
                values.append("")
        rows.append(values)

    return rows


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
            first_name="Ana",
            last_name="Lopez Gomez",
        )
        _employee_two_user, employee_two = self.create_employee_user(
            email="employee-export-two@example.com",
            dni="99999999R",
            first_name="Carlos",
            last_name="Fuera Lista",
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
        mail.outbox.clear()

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
        expected_file_name_pattern = (
            rf"vacation_{timezone.localdate().isoformat()}_[0-9a-f]{{6}}\.xlsx"
        )
        content_disposition = response["Content-Disposition"]
        file_name_match = re.search(expected_file_name_pattern, content_disposition)
        self.assertIsNotNone(file_name_match)
        self.assertEqual(mail.outbox, [])

        export_history = ExportHistory.objects.get()
        self.assertEqual(
            export_history.export_type,
            EXPORT_TYPE_RRHH_VACATION_REQUESTS,
        )
        self.assertEqual(export_history.status, "success")
        self.assertEqual(export_history.total_records, 1)
        self.assertEqual(export_history.filters_json["status"], "pending")
        self.assertRegex(export_history.file_name, expected_file_name_pattern)
        self.assertEqual(
            export_history.columns_version,
            "rrhh_vacation_requests_v1",
        )
        self.assertEqual(
            export_history.rows_snapshot_json,
            [
                {
                    "employee_number": "88888888Y",
                    "last_name": "Lopez Gomez",
                    "first_name": "Ana",
                    "start_date": "01-07-2026",
                    "end_date": "05-07-2026",
                    "phone": "600123123",
                    "requested_days": 5,
                }
            ],
        )

        rows = _read_sheet_rows(response.content)
        self.assertEqual(
            rows,
            [
                [
                    "Numero empleado",
                    "Apellidos",
                    "Nombre",
                    "Fecha inicio",
                    "Fecha final",
                    "Telefono",
                    "Dias solicitados",
                ],
                [
                    "88888888Y",
                    "Lopez Gomez",
                    "Ana",
                    "01-07-2026",
                    "05-07-2026",
                    "600123123",
                    "5",
                ],
            ],
        )
        sheet_xml = _read_workbook_file(response.content, "xl/worksheets/sheet1.xml")
        sheet_root = ElementTree.fromstring(sheet_xml)
        columns = sheet_root.findall(".//sheet:col", XLSX_NAMESPACE)
        self.assertEqual(
            [column.attrib["width"] for column in columns],
            ["18", "30", "22", "16", "16", "18", "18"],
        )
        self.assertEqual(
            [column.attrib["customWidth"] for column in columns],
            ["1", "1", "1", "1", "1", "1", "1"],
        )
        header_cells = sheet_root.findall(
            ".//sheet:row[@r='1']/sheet:c",
            XLSX_NAMESPACE,
        )
        self.assertTrue(header_cells)
        self.assertTrue(all(cell.attrib.get("s") == "1" for cell in header_cells))
        requested_days_cell = sheet_root.find(".//sheet:c[@r='G2']", XLSX_NAMESPACE)
        self.assertIsNotNone(requested_days_cell)
        self.assertNotIn("t", requested_days_cell.attrib)

        styles_xml = _read_workbook_file(response.content, "xl/styles.xml")
        self.assertIn("<b/>", styles_xml)
        self.assertIn('<cellXfs count="2">', styles_xml)

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

    def test_excel_keeps_current_columns_but_respects_seniority_order(self):
        rrhh_user = self.create_rrhh_user(
            email="rrhh-export-order@example.com",
            dni="11111111H",
        )
        _older_user, older_employee = self.create_employee_user(
            email="employee-export-older@example.com",
            dni="12121212M",
            first_name="Sonia",
            last_name="Veterana",
            hire_date=date(2020, 1, 1),
        )
        _younger_user, younger_employee = self.create_employee_user(
            email="employee-export-younger@example.com",
            dni="23232323T",
            first_name="Mario",
            last_name="Reciente",
            hire_date=date(2024, 1, 1),
        )

        VacationRequest.objects.create(
            employee=younger_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 10),
            end_date=date(2026, 7, 14),
            requested_days="5.00",
        )
        VacationRequest.objects.create(
            employee=older_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )

        self.client.force_login(rrhh_user)

        response = self.client.get(
            reverse("vacations:export-rrhh-requests-excel"),
            {"status": "pending"},
        )

        self.assertEqual(response.status_code, 200)

        rows = _read_sheet_rows(response.content)
        self.assertEqual(
            rows[0],
            [
                "Numero empleado",
                "Apellidos",
                "Nombre",
                "Fecha inicio",
                "Fecha final",
                "Telefono",
                "Dias solicitados",
            ],
        )
        self.assertNotIn("Dias seleccionados", rows[0])
        self.assertNotIn("Estado", rows[0])
        self.assertNotIn("Fecha alta", rows[0])
        self.assertNotIn("Observaciones", rows[0])
        self.assertEqual(
            [row[1] for row in rows[1:]],
            ["Veterana", "Reciente"],
        )
