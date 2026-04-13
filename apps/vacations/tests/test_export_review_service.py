"""Tests de la capa de revision previa a la exportacion de RRHH."""

from datetime import date

from apps.vacations.models import VacationRequest, VacationStatus
from apps.vacations.services.export.review import build_rrhh_export_review

from .base import VacationBaseTestCase


class ExportReviewServiceTests(VacationBaseTestCase):
    """Comprueba el enriquecimiento previo al panel y la exportacion."""

    @classmethod
    def setUpTestData(cls):
        cls.pending_status = VacationStatus.objects.get(name="pending")
        cls.approved_status = VacationStatus.objects.get(name="approved")
        cls.rejected_status = VacationStatus.objects.get(name="rejected")

    def test_review_detects_overlaps_with_other_department_employees(self):
        department = self.create_department(name="Operaciones")
        _main_user, main_employee = self.create_employee_user(
            email="review-main@example.com",
            dni="12345678Z",
            department=department,
            first_name="Lucia",
            last_name="Martin",
        )
        _other_user, other_employee = self.create_employee_user(
            email="review-other@example.com",
            dni="00000000T",
            department=department,
            first_name="Carlos",
            last_name="Ruiz",
        )
        _third_user, third_employee = self.create_employee_user(
            email="review-third@example.com",
            dni="22222222J",
            department=department,
            first_name="Marta",
            last_name="Vega",
        )

        main_request = VacationRequest.objects.create(
            employee=main_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )
        VacationRequest.objects.create(
            employee=other_employee,
            status=self.approved_status,
            start_date=date(2026, 7, 3),
            end_date=date(2026, 7, 6),
            requested_days="4.00",
        )
        VacationRequest.objects.create(
            employee=other_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 4),
            end_date=date(2026, 7, 7),
            requested_days="4.00",
        )
        VacationRequest.objects.create(
            employee=third_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 2),
            end_date=date(2026, 7, 4),
            requested_days="3.00",
        )

        export_review = build_rrhh_export_review([main_request])
        reviewed_request = export_review["vacation_requests"][0]

        self.assertEqual(reviewed_request.department_overlap_employees_count, 2)
        self.assertIn("Coincide con 2 empleados", reviewed_request.export_review_observations)
        self.assertEqual(
            export_review["summary"]["department_overlap_requests_count"],
            1,
        )

    def test_review_ignores_rejected_requests_when_calculating_overlaps(self):
        department = self.create_department(name="Limpieza")
        _main_user, main_employee = self.create_employee_user(
            email="review-rejected-main@example.com",
            dni="33333333P",
            department=department,
        )
        _other_user, other_employee = self.create_employee_user(
            email="review-rejected-other@example.com",
            dni="44444444A",
            department=department,
        )

        main_request = VacationRequest.objects.create(
            employee=main_employee,
            status=self.pending_status,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 5),
            requested_days="5.00",
        )
        VacationRequest.objects.create(
            employee=other_employee,
            status=self.rejected_status,
            start_date=date(2026, 8, 2),
            end_date=date(2026, 8, 4),
            requested_days="3.00",
        )

        export_review = build_rrhh_export_review([main_request])
        reviewed_request = export_review["vacation_requests"][0]

        self.assertEqual(reviewed_request.department_overlap_employees_count, 0)
        self.assertNotIn(
            "Coincide con 1 empleado",
            reviewed_request.export_review_observations,
        )

    def test_review_does_not_calculate_department_overlap_without_department(self):
        _main_user, main_employee = self.create_employee_user(
            email="review-nodept-main@example.com",
            dni="55555555K",
        )
        department = self.create_department(name="Mantenimiento")
        _other_user, other_employee = self.create_employee_user(
            email="review-nodept-other@example.com",
            dni="66666666Q",
            department=department,
        )

        main_request = VacationRequest.objects.create(
            employee=main_employee,
            status=self.pending_status,
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 12),
            requested_days="3.00",
        )
        VacationRequest.objects.create(
            employee=other_employee,
            status=self.approved_status,
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 12),
            requested_days="3.00",
        )

        export_review = build_rrhh_export_review([main_request])
        reviewed_request = export_review["vacation_requests"][0]

        self.assertEqual(reviewed_request.department_overlap_employees_count, 0)
        self.assertNotIn(
            "Coincide con 1 empleado",
            reviewed_request.export_review_observations,
        )

    def test_review_marks_high_load_periods_by_real_date_intersection(self):
        department = self.create_department(name="Servicios")
        _summer_user, summer_employee = self.create_employee_user(
            email="review-summer@example.com",
            dni="77777777B",
            department=department,
        )
        _christmas_user, christmas_employee = self.create_employee_user(
            email="review-christmas@example.com",
            dni="88888888Y",
            department=department,
        )

        summer_request = VacationRequest.objects.create(
            employee=summer_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 20),
            end_date=date(2026, 7, 24),
            requested_days="5.00",
        )
        christmas_request = VacationRequest.objects.create(
            employee=christmas_employee,
            status=self.pending_status,
            start_date=date(2026, 12, 20),
            end_date=date(2026, 12, 24),
            requested_days="5.00",
        )

        export_review = build_rrhh_export_review([summer_request, christmas_request])
        reviewed_requests = export_review["vacation_requests"]

        self.assertEqual(reviewed_requests[0].high_load_period_labels, ["Verano"])
        self.assertEqual(reviewed_requests[1].high_load_period_labels, ["Navidad"])
        self.assertEqual(export_review["summary"]["high_load_requests_count"], 2)

    def test_review_marks_only_requests_with_exactly_thirty_days_as_long_duration(self):
        department = self.create_department(name="RRHH")
        _long_user, long_employee = self.create_employee_user(
            email="review-long@example.com",
            dni="99999999R",
            department=department,
        )
        _short_user, short_employee = self.create_employee_user(
            email="review-short@example.com",
            dni="10101010P",
            department=department,
        )

        long_request = VacationRequest.objects.create(
            employee=long_employee,
            status=self.pending_status,
            start_date=date(2026, 6, 15),
            end_date=date(2026, 7, 14),
            requested_days="30.00",
        )
        short_request = VacationRequest.objects.create(
            employee=short_employee,
            status=self.pending_status,
            start_date=date(2026, 6, 15),
            end_date=date(2026, 7, 13),
            requested_days="29.00",
        )

        export_review = build_rrhh_export_review([long_request, short_request])
        reviewed_requests = {
            vacation_request.pk: vacation_request
            for vacation_request in export_review["vacation_requests"]
        }

        self.assertTrue(reviewed_requests[long_request.pk].is_long_duration)
        self.assertIn(
            "Larga duracion",
            reviewed_requests[long_request.pk].export_review_observations,
        )
        self.assertFalse(reviewed_requests[short_request.pk].is_long_duration)
        self.assertEqual(export_review["summary"]["long_duration_requests_count"], 1)

    def test_review_orders_requests_by_seniority_then_start_date_and_creation(self):
        department = self.create_department(name="Cocina")
        _young_user, young_employee = self.create_employee_user(
            email="review-order-young@example.com",
            dni="12121212M",
            department=department,
            first_name="Berta",
            last_name="Joven",
            hire_date=date(2024, 2, 1),
        )
        _old_user, old_employee = self.create_employee_user(
            email="review-order-old@example.com",
            dni="13579135G",
            department=department,
            first_name="Alba",
            last_name="Veterana",
            hire_date=date(2020, 1, 10),
        )

        young_request = VacationRequest.objects.create(
            employee=young_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 15),
            end_date=date(2026, 7, 18),
            requested_days="4.00",
        )
        old_late_request = VacationRequest.objects.create(
            employee=old_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 20),
            end_date=date(2026, 7, 23),
            requested_days="4.00",
        )
        old_early_first_request = VacationRequest.objects.create(
            employee=old_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 5),
            end_date=date(2026, 7, 8),
            requested_days="4.00",
        )
        old_early_second_request = VacationRequest.objects.create(
            employee=old_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 5),
            end_date=date(2026, 7, 8),
            requested_days="4.00",
        )

        export_review = build_rrhh_export_review(
            [
                young_request,
                old_late_request,
                old_early_second_request,
                old_early_first_request,
            ]
        )
        ordered_ids = [
            vacation_request.pk for vacation_request in export_review["vacation_requests"]
        ]

        self.assertEqual(
            ordered_ids,
            [
                old_early_first_request.pk,
                old_early_second_request.pk,
                old_late_request.pk,
                young_request.pk,
            ],
        )
