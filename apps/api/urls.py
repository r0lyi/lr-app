"""URLs de la API interna autenticada por JWT."""

from django.urls import path

from apps.api.views.dashboard import (
    request_kpis_view,
    user_kpis_view,
)
from apps.api.views.users import user_summary_view

app_name = "api"

urlpatterns = [
    path("dashboard/solicitudes/kpis/", request_kpis_view, name="request-kpis"),
    path("dashboard/usuarios/kpis/", user_kpis_view, name="user-kpis"),
    path("usuarios/<int:user_id>/resumen/", user_summary_view, name="user-summary"),
]
