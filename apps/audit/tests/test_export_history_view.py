"""Tests basicos de la vista de historial de exportaciones."""

from django.urls import reverse

from apps.audit.services import (
    EXPORT_TYPE_RRHH_VACATION_REQUESTS,
    create_export_history,
    mark_export_success,
)
from apps.users.models import User

from apps.dashboard.tests.base import DashboardRoleBaseTestCase


class ExportHistoryViewTests(DashboardRoleBaseTestCase):
    """Verifica que RRHH puede consultar el historial exportado."""

    def create_rrhh_user(self, *, email, dni):
        """Crea un usuario RRHH reutilizable en los tests del historial."""

        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        user.roles.set([self.rrhh_role])
        return user

    def test_rrhh_can_open_export_history_view(self):
        rrhh_user = self.create_rrhh_user(
            email="rrhh-history@example.com",
            dni="66666666Q",
        )
        export_history = create_export_history(
            user=rrhh_user,
            export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
            filters={"status": "pending"},
        )
        mark_export_success(
            export_history=export_history,
            file_name="solicitudes_prueba.xlsx",
            file_bytes=b"excel-content",
            total_records=2,
        )

        self.client.force_login(rrhh_user)

        response = self.client.get(reverse("audit:export-history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Historial de exportaciones")
        self.assertContains(response, "solicitudes_prueba.xlsx")
        self.assertContains(response, "2")
        self.assertContains(response, "Cantidad de solicitudes")
        self.assertNotContains(response, "Filtros")
        self.assertNotContains(response, "Estado")
        self.assertNotContains(response, "Tipo")
        self.assertContains(
            response,
            reverse("audit:download-export", args=[export_history.pk]),
        )

    def test_rrhh_can_download_a_previous_export(self):
        rrhh_user = self.create_rrhh_user(
            email="rrhh-history-download@example.com",
            dni="55555555K",
        )
        export_history = create_export_history(
            user=rrhh_user,
            export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
            filters={"status": "pending"},
        )
        mark_export_success(
            export_history=export_history,
            file_name="solicitudes_descarga.xlsx",
            file_bytes=b"excel-download-content",
            total_records=1,
        )

        self.client.force_login(rrhh_user)

        response = self.client.get(
            reverse("audit:download-export", args=[export_history.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertIn("solicitudes_descarga.xlsx", response["Content-Disposition"])
        self.assertEqual(
            b"".join(response.streaming_content),
            b"excel-download-content",
        )
