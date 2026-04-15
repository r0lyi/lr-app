"""Vista basica del perfil del usuario dentro del dominio de empleados."""

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.employees.forms import EmployeeProfileUpdateForm
from apps.employees.selectors import get_employee_profile_for_user
from apps.users.selectors import get_primary_role


@login_required(login_url="/auth/login/")
def employee_profile_view(request):
    """Muestra la ficha `Employee` asociada al usuario autenticado.

    La vista es intencionadamente simple:
    - cualquier usuario autenticado puede abrir su opcion de perfil
    - si tiene una ficha `Employee`, se muestra toda la informacion basica
    - permite cambiar la contrasena del usuario autenticado desde el perfil
    - si no tiene ficha y su rol es employee, se le redirige a onboarding
    - si no tiene ficha y pertenece a otro rol, se muestra un mensaje claro
    """
    current_role = get_primary_role(request.user)
    if not current_role:
        return redirect("dashboard:error-400")

    employee_profile = get_employee_profile_for_user(request.user)
    if employee_profile is None and current_role == "employee":
        return redirect("employees:onboarding")

    # El perfil se presenta como formulario editable por defecto.
    profile_edit_mode = True

    employee_form = (
        EmployeeProfileUpdateForm(instance=employee_profile)
        if employee_profile is not None
        else None
    )
    password_form = PasswordChangeForm(request.user)

    if request.method == "POST":
        profile_action = request.POST.get("profile_action", "password-change")

        if profile_action == "employee-update" and employee_profile is not None:
            # Solo la ficha Employee puede editar estos datos. Dejamos el
            # formulario de contrasena intacto para que no muestre errores
            # ajenos cuando el usuario solo esta actualizando su perfil.
            employee_form = EmployeeProfileUpdateForm(
                request.POST,
                instance=employee_profile,
            )
            profile_edit_mode = True
            if employee_form.is_valid():
                employee_form.save()
                messages.success(
                    request,
                    "Tus datos de empleado se han actualizado correctamente.",
                )
                return redirect("employees:profile")
        else:
            # El cambio de contrasena usa su propio formulario y mantiene la
            # sesion abierta si el cambio se completa correctamente.
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(
                    request,
                    "Tu contrasena se ha actualizado correctamente.",
                )
                return redirect("employees:profile")

    context = build_dashboard_base_context(
        request.user,
        current_role,
        request=request,
        active_section="profile",
        extra_context={
            "employee_profile": employee_profile,
            "employee_form": employee_form,
            "password_form": password_form,
            "profile_edit_mode": profile_edit_mode,
        },
    )
    return render(request, "employees/pages/profile.html", context)
