"""Servicios para preparar el resumen basico del panel de empleado.

La idea clave de este modulo es no mezclar dos conceptos distintos:

1. "Dias anuales de vacaciones":
   El derecho total que corresponde al trabajador dentro del ano natural.
   En nuestro sistema leemos ese valor desde la politica central de vacaciones.
   Hoy esta fijado en 30 dias naturales al ano, que es el minimo legal del
   articulo 38 del Estatuto de los Trabajadores y, ademas, encaja con el
   criterio que estamos usando para este proyecto.

2. "Saldo disponible actual":
   Lo que queda libre despues de descontar vacaciones ya disfrutadas o
   aprobadas. Ese calculo real llegara mas adelante, cuando el flujo completo
   de solicitudes este terminado.

Por eso, en esta primera version del dashboard NO mostramos un saldo restante.
Mostramos el derecho anual del ano en curso. Si la persona ya estaba contratada
antes de empezar el ano, el sistema ensena 30 dias. Si se incorporo durante el
ano en curso, se prorratea desde su fecha de alta hasta el 31 de diciembre.
"""

from calendar import isleap
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from apps.vacations.services.requests.policies import FULL_ANNUAL_VACATION_DAYS
from apps.vacations.selectors import (
    get_employee_vacation_requests,
    get_filtered_employee_vacation_requests,
)


def get_days_in_year(year):
    """Devuelve el numero total de dias del ano natural indicado."""
    return 366 if isleap(year) else 365


def calculate_annual_vacation_days_for_year(hire_date, *, year):
    """Calcula los dias de vacaciones generados dentro de un ano natural.

    Regla aplicada en esta fase del proyecto:
    - Si la persona ya estaba contratada el 1 de enero o antes, le corresponden
      30 dias naturales completos para ese ano.
    - Si entra durante el ano, se prorratea desde la fecha de alta hasta el
      31 de diciembre, ambos inclusive.

    Este valor representa el derecho anual del ejercicio, no el saldo restante.
    Por eso no descuenta vacaciones pendientes, aprobadas ni disfrutadas.
    """
    if hire_date is None:
        return FULL_ANNUAL_VACATION_DAYS

    start_of_year = date(year, 1, 1)
    end_of_year = date(year, 12, 31)

    # Si el alta es posterior al ano consultado, todavia no se genera derecho
    # dentro de ese ejercicio natural.
    if hire_date > end_of_year:
        return Decimal("0.00")

    # Si la fecha de alta cae dentro del ano actual, empezamos a contar desde
    # ese dia. Si el trabajador ya estaba antes, su derecho anual es completo.
    effective_start = max(hire_date, start_of_year)
    days_worked_in_year = (end_of_year - effective_start).days + 1
    proportional_days = (
        FULL_ANNUAL_VACATION_DAYS * Decimal(days_worked_in_year) / Decimal(get_days_in_year(year))
    )

    return proportional_days.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def build_employee_dashboard_summary(employee_profile, *, request_filters=None):
    """Compone el resumen simple mostrado en la home del empleado.

    Este resumen intenta responder a cuatro preguntas muy concretas:
    - cuantas solicitudes siguen pendientes
    - cuantos dias de vacaciones genera este empleado en el ano natural
    - cual fue la ultima resolucion registrada
    - que solicitudes tiene ya guardadas en el sistema
    """
    employee_requests = get_employee_vacation_requests(employee_profile)
    current_year = timezone.localdate().year
    latest_request = employee_requests.first()
    latest_resolved_request = employee_requests.filter(
        resolution_date__isnull=False,
    ).order_by("-resolution_date").first()
    annual_vacation_days_count = calculate_annual_vacation_days_for_year(
        employee_profile.hire_date,
        year=current_year,
    )
    annual_vacation_progress_percent = Decimal("0.00")
    if FULL_ANNUAL_VACATION_DAYS:
        annual_vacation_progress_percent = (
            annual_vacation_days_count / FULL_ANNUAL_VACATION_DAYS * Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        annual_vacation_progress_percent = min(
            annual_vacation_progress_percent,
            Decimal("100.00"),
        )

    request_filters = request_filters or {}
    filtered_employee_requests = get_filtered_employee_vacation_requests(
        employee_profile,
        start_date=request_filters.get("start_date"),
        end_date=request_filters.get("end_date"),
        status_name=request_filters.get("status"),
    )

    if latest_resolved_request is None:
        latest_resolution_summary = "Todavía no tienes solicitudes resueltas."
    elif latest_resolved_request.status.name == "approved":
        latest_resolution_summary = "Tu última solicitud fue aprobada por RRHH."
    else:
        latest_resolution_summary = "Tu última solicitud fue rechazada por RRHH."

    return {
        "employee_profile": employee_profile,
        "employee_requests_count": employee_requests.count(),
        "pending_requests_count": employee_requests.filter(status__name="pending").count(),
        "annual_vacation_days_count": annual_vacation_days_count,
        "annual_vacation_reference_year": current_year,
        "annual_vacation_progress_percent": annual_vacation_progress_percent,
        "latest_request": latest_request,
        "latest_resolution": latest_resolved_request,
        "latest_resolution_summary": latest_resolution_summary,
        "employee_requests": filtered_employee_requests,
    }
