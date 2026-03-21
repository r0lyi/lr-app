"""Helpers compartidos para construir datos basicos del layout del dashboard."""

from apps.employees.models import Employee


def get_dashboard_display_name(user):
    """Devuelve un nombre legible para el encabezado del dashboard."""
    try:
        profile = user.employee_profile
    except Employee.DoesNotExist:
        profile = None

    if profile is not None:
        full_name = f"{profile.first_name} {profile.last_name}".strip()
        if full_name:
            return full_name

    email = (user.email or "").strip()
    if "@" in email:
        return email.split("@", 1)[0]
    return email or "Usuario"
