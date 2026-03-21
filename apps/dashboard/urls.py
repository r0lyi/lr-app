from django.urls import path

from .views import (
    admin_home_view,
    employee_home_view,
    error_400_view,
    home_view,
    rrhh_home_view,
)

app_name = "dashboard"

urlpatterns = [
    path("", home_view, name="home"),
    path("employee/", employee_home_view, name="employee-home"),
    path("rrhh/", rrhh_home_view, name="rrhh-home"),
    path("admin/", admin_home_view, name="admin-home"),
    path("error-400/", error_400_view, name="error-400"),
]
