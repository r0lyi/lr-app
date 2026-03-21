"""Tests del servicio que calcula el resumen basico del panel de empleado."""

from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.employees.services.employee_dashboard import (
    calculate_annual_vacation_days_for_year,
)


class EmployeeDashboardServiceTests(TestCase):
    """Comprueba la logica anual de vacaciones mostrada en el dashboard."""

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
