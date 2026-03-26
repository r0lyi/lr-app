"""Vista basica del perfil del usuario dentro del dominio de empleados."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.dashboard.services.layout_context import build_dashboard_base_context
from apps.employees.selectors import get_employee_profile_for_user
from apps.users.selectors import get_primary_role


@login_required(login_url="/auth/login/")
def employee_profile_view(request):
    """Muestra la ficha `Employee` asociada al usuario autenticado.

    La vista es intencionadamente simple:
    - cualquier usuario autenticado puede abrir su opcion de perfil
    - si tiene una ficha `Employee`, se muestra toda la informacion basica
    - si no tiene ficha y su rol es employee, se le redirige a onboarding
    - si no tiene ficha y pertenece a otro rol, se muestra un mensaje claro
    """
    current_role = get_primary_role(request.user)
    if not current_role:
        return redirect("dashboard:error-400")

    employee_profile = get_employee_profile_for_user(request.user)
    if employee_profile is None and current_role == "employee":
        return redirect("employees:onboarding")

    context = build_dashboard_base_context(
        request.user,
        current_role,
        active_section="profile",
        extra_context={
            "employee_profile": employee_profile,
        },
    )
    return render(request, "employees/profile.html", context)
