

from django.urls import path
from .views.auth_views import (
    login_view,
    logout_view,
    request_activation_view,
    set_password_view,
)

# Namespace para las URLs de autenticación
app_name = "auth"

# URLs relacionadas con autenticación, activación de cuenta y gestión de tokens
urlpatterns = [
    # URL para solicitar activación de cuenta, con limitación de intentos
    path("activate/", request_activation_view, name="request-activation"),
    # URL para establecer contraseña usando el token de activación
    path("set-password/<str:token>/", set_password_view, name="set-password"),
    # URL para login, usando el backend personalizado que autentica por DNI
    path("login/", login_view, name="login"),
    # URL para logout, que cierra la sesión del usuario
    path("logout/", logout_view, name="logout"),
]
