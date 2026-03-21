from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.employees.models import Employee


@login_required(login_url="/auth/login/")
def home_view(request):
    try:
        employee_profile = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect("employees:onboarding")

    full_name = f"{employee_profile.first_name} {employee_profile.last_name}".strip()
    context = {
        "employee_profile": employee_profile,
        "user_display_name": full_name or request.user.email,
    }
    return render(request, "dashboard/home.html", context)
