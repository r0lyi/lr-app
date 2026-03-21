"""Servicios para preparar el resumen basico del panel de empleado."""

from apps.employees.selectors.employee_dashboard import get_employee_requests

DEFAULT_AVAILABLE_DAYS = 30


def build_employee_dashboard_summary(employee_profile):
    """Compone el resumen simple mostrado en la home del empleado."""
    employee_requests = get_employee_requests(employee_profile)
    latest_resolved_request = employee_requests.filter(
        resolution_date__isnull=False,
    ).order_by("-resolution_date").first()

    return {
        "employee_profile": employee_profile,
        "pending_requests_count": employee_requests.filter(status__name="pending").count(),
        "available_days_count": (
            employee_profile.available_days or DEFAULT_AVAILABLE_DAYS
        ),
        "latest_resolution": latest_resolved_request,
        "employee_requests": employee_requests,
    }
