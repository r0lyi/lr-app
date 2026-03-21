from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.employees.forms import EmployeeOnboardingForm
from apps.employees.models import Employee


@login_required(login_url="/auth/login/")
def onboarding_view(request):
    user = request.user

    try:
        profile = user.employee_profile
    except Employee.DoesNotExist:
        profile = None

    if profile and request.method == "GET":
        return redirect("dashboard:home")

    initial = {
        "first_name": profile.first_name if profile else "",
        "last_name": profile.last_name if profile else "",
        "email": user.email or "",
        "phone": profile.phone if profile else "",
        "hire_date": profile.hire_date.isoformat() if profile and profile.hire_date else "",
    }

    if request.method == "POST":
        form = EmployeeOnboardingForm(request.POST, user=user)
        if form.is_valid():
            data = form.cleaned_data

            if profile is None:
                profile = Employee(user=user)

            profile.first_name = data["first_name"].strip()
            profile.last_name = data["last_name"].strip()
            profile.phone = data["phone"].strip() if data["phone"] else None
            profile.hire_date = data["hire_date"]
            profile.save()

            if data["email"] and data["email"] != user.email:
                user.email = data["email"]
                user.save(update_fields=["email"])

            messages.success(request, "Tu perfil de empleado se ha guardado correctamente.")
            return redirect("dashboard:home")
    else:
        form = EmployeeOnboardingForm(initial=initial, user=user)

    return render(request, "employees/onboarding.html", {"form": form})
