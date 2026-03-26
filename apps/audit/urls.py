"""URLs del dominio de auditoria."""

from django.urls import path

from apps.audit.views import (
    download_export_history_file_view,
    export_history_view,
)

app_name = "audit"

urlpatterns = [
    path("exports/", export_history_view, name="export-history"),
    path(
        "exports/<int:export_history_id>/download/",
        download_export_history_file_view,
        name="download-export",
    ),
]
