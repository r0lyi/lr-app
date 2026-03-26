"""Rutas del flujo de onboarding de empleados."""

from django.urls import path

from apps.employees.views.onboarding import onboarding_view
from apps.employees.views.view_profile import employee_profile_view

app_name = "employees"

urlpatterns = [
    path("onboarding/", onboarding_view, name="onboarding"),
    path("profile/", employee_profile_view, name="profile"),
]
