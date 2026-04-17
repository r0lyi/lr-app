"""Tests basicos de la vista de historial de exportaciones."""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

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

    def test_rrhh_can_filter_export_history_by_date_range(self):
        rrhh_user = self.create_rrhh_user(
            email="rrhh-history-filter@example.com",
            dni="44444444A",
        )
        recent_export = create_export_history(
            user=rrhh_user,
            export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
            filters={"status": "pending"},
        )
        mark_export_success(
            export_history=recent_export,
            file_name="vacation_26-03-2026.xlsx",
            file_bytes=b"recent-file",
            total_records=3,
        )

        old_export = create_export_history(
            user=rrhh_user,
            export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
            filters={"status": "approved"},
        )
        mark_export_success(
            export_history=old_export,
            file_name="vacation_15-02-2026.xlsx",
            file_bytes=b"old-file",
            total_records=1,
        )

        old_created_at = timezone.now() - timedelta(days=40)
        recent_created_at = timezone.now() - timedelta(days=2)
        type(old_export).objects.filter(pk=old_export.pk).update(
            created_at=old_created_at
        )
        type(recent_export).objects.filter(pk=recent_export.pk).update(
            created_at=recent_created_at
        )

        self.client.force_login(rrhh_user)

        response = self.client.get(
            reverse("audit:export-history"),
            {
                "start_date": (timezone.localdate() - timedelta(days=7)).isoformat(),
                "end_date": timezone.localdate().isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "vacation_26-03-2026.xlsx")
        self.assertNotContains(response, "vacation_15-02-2026.xlsx")

    def test_export_history_is_paginated_by_ten(self):
        rrhh_user = self.create_rrhh_user(
            email="rrhh-history-pagination@example.com",
            dni=self.build_valid_dni(32000000),
        )
        for index in range(12):
            export_history = create_export_history(
                user=rrhh_user,
                export_type=EXPORT_TYPE_RRHH_VACATION_REQUESTS,
                filters={"status": "pending"},
            )
            mark_export_success(
                export_history=export_history,
                file_name=f"solicitudes_paginadas_{index:02d}.xlsx",
                file_bytes=b"excel-content",
                total_records=index + 1,
            )

        self.client.force_login(rrhh_user)

        first_page = self.client.get(reverse("audit:export-history"))
        second_page = self.client.get(
            reverse("audit:export-history"),
            {"page": "2"},
        )

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(first_page.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(first_page.context["filtered_exports_count"], 12)
        self.assertEqual(len(first_page.context["export_histories"]), 10)
        self.assertContains(first_page, "Mostrando 1-10 de 12 exportaciones")

        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(second_page.context["export_histories"]), 2)
        self.assertContains(second_page, "Mostrando 11-12 de 12 exportaciones")

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
