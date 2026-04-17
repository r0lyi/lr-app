"""Tests de enrutado principal del dashboard segun el rol."""

from datetime import date

from django.urls import reverse

from .base import DashboardRoleBaseTestCase


class DashboardRoutingTests(DashboardRoleBaseTestCase):
    """Comprueba a que home se redirige desde dashboard:home."""

    def test_employee_without_profile_is_redirected_to_onboarding(self):
        user = self.create_active_user(
            email="employee-no-profile@example.com",
            dni="12345678Z",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("employees:onboarding"))
        self.assertEqual(list(user.roles.values_list("name", flat=True)), ["employee"])

    def test_rrhh_without_profile_is_redirected_to_onboarding(self):
        user = self.create_active_user(
            email="rrhh-no-profile@example.com",
            dni="11111111H",
        )
        user.roles.set([self.rrhh_role])

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("employees:onboarding"))

    def test_admin_without_profile_is_redirected_to_onboarding(self):
        user = self.create_active_user(
            email="admin-no-profile@example.com",
            dni="22222222J",
        )
        user.roles.set([self.admin_role])

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("employees:onboarding"))

    def test_employee_with_profile_is_redirected_to_employee_home(self):
        user = self.create_active_user(
            email="employee-with-profile@example.com",
            dni="00000000T",
        )
        self.create_employee_profile(user)

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:employee-home"))

        employee_home = self.client.get(reverse("dashboard:employee-home"))
        self.assertEqual(employee_home.status_code, 200)
        self.assertContains(employee_home, "Panel de empleado")
        self.assertContains(employee_home, "Ana")
        self.assertContains(employee_home, "Solicitudes Pendientes")
        self.assertContains(employee_home, "Vacaciones disponibles")
        self.assertContains(
            employee_home,
            '<strong class="employee-home-summary-card__value">30</strong>',
            html=True,
        )
        self.assertContains(employee_home, "Ultima Resolucion")
        self.assertContains(employee_home, "Sin resoluciones")
        self.assertContains(
            employee_home,
            "No hay solicitudes registradas con estos filtros.",
        )
        self.assertContains(employee_home, "Desde")
        self.assertContains(employee_home, "Hasta")
        self.assertContains(employee_home, "Estado")
        self.assertContains(employee_home, "Filtrar")
        self.assertContains(employee_home, "Limpiar")
        self.assertContains(employee_home, "Rango de fechas")
        self.assertContains(employee_home, "Total días")

    def test_employee_home_subtracts_active_requests_from_available_days(self):
        user = self.create_active_user(
            email="employee-balance-home@example.com",
            dni="12345678Z",
        )
        employee = self.create_employee_profile(user)
        self.create_vacation_request(
            employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )
        self.create_vacation_request(
            employee,
            status=self.approved_status,
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 12),
            requested_days="3.00",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:employee-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vacaciones disponibles")
        self.assertContains(
            response,
            '<strong class="employee-home-summary-card__value">22</strong>',
            html=True,
        )
        self.assertContains(response, "8.00 días solicitados")

    def test_employee_home_filters_requests_by_dates_and_status(self):
        user = self.create_active_user(
            email="employee-filter@example.com",
            dni="13579135G",
        )
        employee = self.create_employee_profile(user)
        self.create_vacation_request(
            employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )
        self.create_vacation_request(
            employee,
            status=self.approved_status,
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 12),
            requested_days="3.00",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("dashboard:employee-home"),
            {
                "start_date": "2026-08-01",
                "end_date": "2026-08-31",
                "status": "approved",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10-08-2026")
        self.assertContains(response, "12-08-2026")
        self.assertContains(response, "Aprobada")
        self.assertContains(response, "employee-history-table__status--approved")
        self.assertNotContains(response, "01-07-2026")
        self.assertNotContains(response, "05-07-2026")

    def test_employee_home_paginates_requests_by_ten(self):
        user = self.create_active_user(
            email="employee-pagination@example.com",
            dni="23232323T",
        )
        employee = self.create_employee_profile(user)
        for day in range(1, 13):
            self.create_vacation_request(
                employee,
                status=self.pending_status,
                start_date=date(2026, 1, day),
                end_date=date(2026, 1, day),
                requested_days="1.00",
            )

        self.client.force_login(user)

        first_page = self.client.get(reverse("dashboard:employee-home"))
        second_page = self.client.get(
            reverse("dashboard:employee-home"),
            {"page": "2"},
        )

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(first_page.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(first_page.context["filtered_employee_requests_count"], 12)
        self.assertEqual(len(first_page.context["employee_requests"]), 10)
        self.assertContains(first_page, "Mostrando 1-10 de 12 solicitudes")
        self.assertContains(first_page, 'href="?page=2"', html=False)

        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(second_page.context["employee_requests"]), 2)
        self.assertContains(second_page, "Mostrando 11-12 de 12 solicitudes")

    def test_employee_home_shows_delete_action_only_for_pending_requests(self):
        user = self.create_active_user(
            email="employee-delete-action@example.com",
            dni="12121212M",
        )
        employee = self.create_employee_profile(user)
        pending_request = self.create_vacation_request(
            employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )
        approved_request = self.create_vacation_request(
            employee,
            status=self.approved_status,
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 12),
            requested_days="3.00",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:employee-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Acciones")
        self.assertContains(response, "Eliminar solicitud")
        self.assertContains(response, "¿Seguro que quieres eliminar esta solicitud?")
        self.assertContains(
            response,
            reverse("vacations:delete-request", args=[pending_request.pk]),
        )
        self.assertNotContains(
            response,
            reverse("vacations:delete-request", args=[approved_request.pk]),
        )
        self.assertContains(response, "Solo se pueden eliminar solicitudes pendientes")

    def test_rrhh_is_redirected_to_rrhh_home(self):
        user = self.create_active_user(
            email="rrhh@example.com",
            dni="11111111H",
        )
        user.roles.set([self.rrhh_role])
        self.create_employee_profile(
            user,
            first_name="Rosa",
            last_name="Ruiz",
        )
        employee_user = self.create_active_user(
            email="employee-for-rrhh@example.com",
            dni="33333333P",
        )
        employee = self.create_employee_profile(
            employee_user,
            first_name="Lucia",
            last_name="Martinez",
        )
        self.create_vacation_request(
            employee,
            status=self.pending_status,
            start_date=date(2026, 6, 10),
            end_date=date(2026, 6, 14),
            requested_days="5.00",
        )
        approved_employee_user = self.create_active_user(
            email="employee-approved-default@example.com",
            dni="77777777B",
        )
        approved_employee = self.create_employee_profile(
            approved_employee_user,
            first_name="Carlos",
            last_name="Sanchez",
        )
        self.create_vacation_request(
            approved_employee,
            status=self.approved_status,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 3),
            requested_days="3.00",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:rrhh-home"))

        rrhh_home = self.client.get(reverse("dashboard:rrhh-home"))
        self.assertEqual(rrhh_home.status_code, 200)
        self.assertContains(rrhh_home, "Solicitudes")
        self.assertContains(rrhh_home, "Filtrar")
        self.assertContains(rrhh_home, "Limpiar")
        self.assertContains(rrhh_home, "Nombre")
        self.assertContains(rrhh_home, "Apellidos")
        self.assertContains(rrhh_home, "Fecha inicio")
        self.assertContains(rrhh_home, "Fecha final")
        self.assertContains(rrhh_home, "Días")
        self.assertContains(rrhh_home, "Estado")
        self.assertContains(rrhh_home, "Exportar Excel")
        self.assertContains(rrhh_home, "Control de ausencias y vacaciones del personal.")
        self.assertContains(rrhh_home, "Lucia")
        self.assertContains(rrhh_home, "Martinez")
        self.assertContains(rrhh_home, "10-06-2026")
        self.assertContains(rrhh_home, "14-06-2026")
        self.assertContains(rrhh_home, "5.00")
        self.assertContains(rrhh_home, "Pendiente")
        self.assertNotContains(rrhh_home, "Carlos")
        self.assertNotContains(rrhh_home, "Sanchez")
        self.assertNotContains(rrhh_home, "approved</td>", html=False)

    def test_rrhh_home_filters_requests_by_search_dates_and_status(self):
        user = self.create_active_user(
            email="rrhh-filter@example.com",
            dni="44444444A",
        )
        user.roles.set([self.rrhh_role])

        employee_one_user = self.create_active_user(
            email="employee-rrhh-one@example.com",
            dni="55555555K",
        )
        employee_one = self.create_employee_profile(
            employee_one_user,
            first_name="Lucia",
            last_name="Martinez",
        )
        self.create_vacation_request(
            employee_one,
            status=self.pending_status,
            start_date=date(2026, 6, 10),
            end_date=date(2026, 6, 14),
            requested_days="5.00",
        )

        employee_two_user = self.create_active_user(
            email="employee-rrhh-two@example.com",
            dni="66666666Q",
        )
        employee_two = self.create_employee_profile(
            employee_two_user,
            first_name="Carlos",
            last_name="Sanchez",
        )
        self.create_vacation_request(
            employee_two,
            status=self.approved_status,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 3),
            requested_days="3.00",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("dashboard:rrhh-home"),
            {
                "search": "lucia",
                "start_date": "2026-06-01",
                "end_date": "2026-06-30",
                "status": "pending",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lucia")
        self.assertContains(response, "Martinez")
        self.assertContains(response, "10-06-2026")
        self.assertContains(response, "14-06-2026")
        self.assertContains(response, "Pendiente")
        self.assertNotContains(response, "Carlos")
        self.assertNotContains(response, "Sanchez")
        self.assertNotContains(response, "01-08-2026")
        self.assertNotContains(response, "03-08-2026")

    def test_rrhh_requests_are_paginated_by_ten(self):
        rrhh_user = self.create_active_user(
            email="rrhh-pagination@example.com",
            dni=self.build_valid_dni(34000000),
        )
        rrhh_user.roles.set([self.rrhh_role])
        self.create_employee_profile(rrhh_user, first_name="Rosa", last_name="Ruiz")
        for index in range(12):
            employee_user = self.create_active_user(
                email=f"rrhh-pagination-employee-{index:02d}@example.com",
                dni=self.build_valid_dni(34000001 + index),
            )
            employee = self.create_employee_profile(
                employee_user,
                first_name=f"Empleado{index:02d}",
                last_name="Paginado",
            )
            self.create_vacation_request(
                employee,
                status=self.pending_status,
                start_date=date(2026, 5, index + 1),
                end_date=date(2026, 5, index + 1),
                requested_days="1.00",
            )

        self.client.force_login(rrhh_user)

        first_page = self.client.get(reverse("dashboard:rrhh-home"))
        second_page = self.client.get(reverse("dashboard:rrhh-home"), {"page": "2"})

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(first_page.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(first_page.context["filtered_requests_count"], 12)
        self.assertEqual(len(first_page.context["vacation_requests"]), 10)
        self.assertContains(first_page, "Mostrando 1-10 de 12 solicitudes")

        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(second_page.context["vacation_requests"]), 2)
        self.assertContains(second_page, "Mostrando 11-12 de 12 solicitudes")

    def test_rrhh_home_shows_export_review_summary_and_seniority_order(self):
        user = self.create_active_user(
            email="rrhh-review-summary@example.com",
            dni="56565656P",
        )
        user.roles.set([self.rrhh_role])
        department = self.create_department(name="Operaciones")

        older_employee_user = self.create_active_user(
            email="employee-review-older@example.com",
            dni="78787878K",
        )
        older_employee = self.create_employee_profile(
            older_employee_user,
            department=department,
            first_name="Sonia",
            last_name="Veterana",
            hire_date=date(2020, 1, 1),
        )
        younger_employee_user = self.create_active_user(
            email="employee-review-younger@example.com",
            dni="90909090A",
        )
        younger_employee = self.create_employee_profile(
            younger_employee_user,
            department=department,
            first_name="Mario",
            last_name="Reciente",
            hire_date=date(2024, 1, 1),
        )
        overlap_employee_user = self.create_active_user(
            email="employee-review-overlap@example.com",
            dni="10101010P",
        )
        overlap_employee = self.create_employee_profile(
            overlap_employee_user,
            department=department,
            first_name="Carlos",
            last_name="Solape",
            hire_date=date(2023, 1, 1),
        )

        self.create_vacation_request(
            older_employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 30),
            requested_days="30.00",
        )
        self.create_vacation_request(
            younger_employee,
            status=self.pending_status,
            start_date=date(2026, 3, 10),
            end_date=date(2026, 3, 14),
            requested_days="5.00",
        )
        self.create_vacation_request(
            overlap_employee,
            status=self.approved_status,
            start_date=date(2026, 7, 10),
            end_date=date(2026, 7, 12),
            requested_days="3.00",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:rrhh-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alertas e información")
        self.assertContains(response, "solicitudes revisadas")
        self.assertContains(response, "Solapamientos de fechas")
        self.assertContains(response, "Solicitudes de larga duración")
        self.assertContains(response, "Registro detallado")
        self.assertContains(response, "Solapamiento de fechas")
        self.assertContains(response, "Solicitud de larga duración")
        self.assertContains(response, "Carlos Solape")
        self.assertContains(response, "10-07-2026 - 12-07-2026")
        self.assertContains(response, "01-07-2026 - 30-07-2026")
        self.assertNotContains(response, "Ordenado por antigüedad")
        self.assertNotContains(response, "Orden aplicado por antigüedad")
        self.assertNotContains(response, "Periodo de alta carga")
        self.assertNotContains(response, "Resumen antes de exportar")
        self.assertContains(response, "Fecha alta")
        self.assertNotContains(response, "Observaciones")
        self.assertContains(response, "Ver detalles")
        self.assertContains(response, "Total este mes")
        self.assertContains(response, "Pendientes de revisión")
        self.assertContains(response, "Pendiente")
        self.assertContains(response, "01-01-2020")
        self.assertContains(response, "01-01-2024")

        response_html = response.content.decode("utf-8")
        self.assertLess(response_html.index("Sonia"), response_html.index("Mario"))

    def test_admin_is_redirected_to_admin_home(self):
        user = self.create_active_user(
            email="admin@example.com",
            dni="22222222J",
        )
        user.roles.set([self.admin_role])
        self.create_employee_profile(
            user,
            first_name="Admin",
            last_name="Sistema",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(response, reverse("dashboard:admin-home"))

        admin_home = self.client.get(reverse("dashboard:admin-home"))
        self.assertEqual(admin_home.status_code, 200)
        self.assertContains(admin_home, "Panel de administrador")

    def test_admin_can_open_requests_management_with_same_flow_as_rrhh(self):
        user = self.create_active_user(
            email="admin-requests@example.com",
            dni="10101010P",
        )
        user.roles.set([self.admin_role])
        employee_user = self.create_active_user(
            email="employee-for-admin-requests@example.com",
            dni="12121212M",
        )
        employee = self.create_employee_profile(
            employee_user,
            first_name="Lucia",
            last_name="Martinez",
        )
        self.create_vacation_request(
            employee,
            status=self.pending_status,
            start_date=date(2026, 6, 10),
            end_date=date(2026, 6, 14),
            requested_days="5.00",
        )

        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:admin-requests"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solicitudes")
        self.assertContains(response, "Control de ausencias y vacaciones del personal.")
        self.assertContains(response, "Lucia")
        self.assertContains(response, "Martinez")
        self.assertContains(response, "10-06-2026")
        self.assertContains(response, "14-06-2026")
        self.assertContains(response, "Exportar Excel")
