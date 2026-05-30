"""URLs API de autenticacion de usuarios."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.users.api.views import DNITokenObtainPairView, session_token_view

app_name = "api-auth"

urlpatterns = [
    path("token/", DNITokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("session-token/", session_token_view, name="session-token"),
]
