"""Tests del servicio que calcula el resumen basico del panel de empleado."""

from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.employees.models import Employee
from apps.employees.services.employee_dashboard import (
    build_employee_dashboard_summary,
    calculate_annual_vacation_days_for_year,
)
from apps.users.models import User
from apps.vacations.models import VacationRequest, VacationStatus


class EmployeeDashboardServiceTests(TestCase):
    """Comprueba la logica anual de vacaciones mostrada en el dashboard."""

    @classmethod
    def setUpTestData(cls):
        cls.pending_status = VacationStatus.objects.get(name="pending")
        cls.approved_status = VacationStatus.objects.get(name="approved")

    def test_full_year_employee_gets_thirty_days(self):
        current_year = timezone.localdate().year

        result = calculate_annual_vacation_days_for_year(
            date(current_year - 1, 6, 1),
            year=current_year,
        )

        self.assertEqual(result, Decimal("30.00"))

    def test_employee_joining_mid_year_gets_prorated_days(self):
        current_year = timezone.localdate().year

        result = calculate_annual_vacation_days_for_year(
            date(current_year, 7, 1),
            year=current_year,
        )

        # Del 1 de julio al 31 de diciembre se genera solo la parte proporcional
        # del derecho anual de 30 dias naturales.
        self.assertEqual(result, Decimal("15.12"))

    def test_dashboard_summary_subtracts_active_requests_from_balance(self):
        current_year = timezone.localdate().year
        user = User.objects.create_user(
            email="employee-balance@example.com",
            dni="12345678Z",
            password="PruebaSegura123!",
            is_active=True,
        )
        employee = Employee.objects.create(
            user=user,
            first_name="Ana",
            last_name="Lopez",
            phone="600123123",
            hire_date=date(current_year - 1, 6, 1),
        )
        VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(current_year, 7, 1),
            end_date=date(current_year, 7, 5),
            requested_days="5.00",
        )
        VacationRequest.objects.create(
            employee=employee,
            status=self.approved_status,
            start_date=date(current_year, 8, 10),
            end_date=date(current_year, 8, 12),
            requested_days="3.00",
        )

        summary = build_employee_dashboard_summary(employee)

        self.assertEqual(summary["annual_vacation_entitlement_days_count"], Decimal("30.00"))
        self.assertEqual(summary["annual_vacation_reserved_days_count"], Decimal("8.00"))
        self.assertEqual(summary["annual_vacation_remaining_days_count"], Decimal("22.00"))
        self.assertEqual(summary["annual_vacation_days_count"], Decimal("22.00"))
