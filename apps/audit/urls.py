"""URLs del dominio de auditoria."""

from django.urls import path

from apps.audit.views import (
    audit_log_view,
    download_export_history_file_view,
    export_history_view,
    preview_export_history_file_view,
)

app_name = "audit"

urlpatterns = [
    path("activity/", audit_log_view, name="activity-log"),
    path("exports/", export_history_view, name="export-history"),
    path(
        "exports/<int:export_history_id>/preview/",
        preview_export_history_file_view,
        name="preview-export",
    ),
    path(
        "exports/<int:export_history_id>/download/",
        download_export_history_file_view,
        name="download-export",
    ),
]
