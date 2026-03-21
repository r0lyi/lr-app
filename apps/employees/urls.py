from django.urls import path

from apps.employees.views.onboarding import onboarding_view

app_name = "employees"

urlpatterns = [
    path("onboarding/", onboarding_view, name="onboarding"),
]
