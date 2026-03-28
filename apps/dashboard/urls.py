"""Rutas del dispatcher y paneles principales del dashboard."""

from django.urls import path

from .views import (
    admin_home_view,
    admin_user_list_view,
    admin_user_primary_role_update_view,
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
    path("admin/users/", admin_user_list_view, name="admin-users"),
    path(
        "admin/users/<int:user_id>/primary-role/",
        admin_user_primary_role_update_view,
        name="admin-user-primary-role",
    ),
    path("error-400/", error_400_view, name="error-400"),
]
