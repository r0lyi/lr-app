"""Rutas publicas del flujo de autenticacion y activacion."""

from django.urls import path
from .views.auth_views import (
    login_view,
    logout_view,
    request_activation_view,
    set_password_view,
)

app_name = "auth"

urlpatterns = [
    path("activate/", request_activation_view, name="request-activation"),
    path("set-password/<str:token>/", set_password_view, name="set-password"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]
