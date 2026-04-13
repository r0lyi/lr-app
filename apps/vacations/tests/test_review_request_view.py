"""Tests basicos de la revision de solicitudes por parte de RRHH."""

from datetime import date

from django.urls import reverse
from django.utils import timezone

from apps.notifications.models import Notification
from apps.users.models import Role, User
from apps.vacations.models import VacationRequest, VacationStatus

from .base import VacationBaseTestCase


class VacationRequestReviewViewTests(VacationBaseTestCase):
    """Comprueba el acceso basico y la actualizacion desde RRHH."""

    @classmethod
    def setUpTestData(cls):
        cls.rrhh_role = Role.objects.get(name="rrhh")
        cls.admin_role = Role.objects.get(name="admin")
        cls.pending_status = VacationStatus.objects.get(name="pending")
        cls.approved_status = VacationStatus.objects.get(name="approved")

    def create_rrhh_user(self, *, email, dni):
        """Crea un usuario activo con rol principal RRHH."""

        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        user.roles.set([self.rrhh_role])
        return user

    def create_rrhh_user_with_employee_profile(self, *, email, dni):
        """Crea un usuario RRHH que tambien tiene ficha Employee propia."""

        user, employee = self.create_employee_user(email=email, dni=dni)
        user.roles.set([self.rrhh_role])
        return user, employee

    def create_admin_user(self, *, email, dni):
        """Crea un admin activo para revisar solicitudes desde su panel."""

        user = User.objects.create_user(
            email=email,
            dni=dni,
            password="PruebaSegura123!",
            is_active=True,
        )
        user.roles.set([self.admin_role])
        return user

    def test_rrhh_can_open_review_page(self):
        rrhh_user = self.create_rrhh_user(
            email="rrhh-review-open@example.com",
            dni="77777777B",
        )
        _employee_user, employee = self.create_employee_user(
            email="employee-review-open@example.com",
            dni="88888888Y",
        )
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )

        self.client.force_login(rrhh_user)

        response = self.client.get(
            reverse("vacations:review-request", args=[vacation_request.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Revisar solicitud")
        self.assertContains(response, "Ana")
        self.assertContains(response, "Lopez")
        self.assertContains(response, "Guardar revision")

    def test_rrhh_can_update_status_and_dates(self):
        rrhh_user = self.create_rrhh_user(
            email="rrhh-review-update@example.com",
            dni="99999999R",
        )
        _employee_user, employee = self.create_employee_user(
            email="employee-review-update@example.com",
            dni="24681357B",
        )
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )

        self.client.force_login(rrhh_user)

        response = self.client.post(
            reverse("vacations:review-request", args=[vacation_request.pk]),
            {
                "status": str(self.approved_status.pk),
                "start_date": "2026-07-10",
                "end_date": "2026-07-12",
                "hr_comment": "Aprobada con cambio de fechas",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:rrhh-home"))
        vacation_request.refresh_from_db()
        self.assertEqual(vacation_request.status, self.approved_status)
        self.assertEqual(vacation_request.start_date, date(2026, 7, 10))
        self.assertEqual(vacation_request.end_date, date(2026, 7, 12))
        self.assertEqual(str(vacation_request.requested_days), "3.00")
        self.assertEqual(vacation_request.hr_comment, "Aprobada con cambio de fechas")
        self.assertIsNotNone(vacation_request.resolution_date)
        self.assertLessEqual(vacation_request.resolution_date, timezone.now())
        self.assertEqual(vacation_request.resolved_by, rrhh_user)

        notification = Notification.objects.get(user=employee.user)
        self.assertEqual(
            notification.notification_type,
            Notification.Type.VACATION_REQUEST_STATUS,
        )
        self.assertEqual(notification.vacation_request, vacation_request)
        self.assertEqual(notification.previous_status_name, "pending")
        self.assertIn("pending -> approved", notification.message)

    def test_rrhh_editing_dates_without_status_change_does_not_notify_employee(self):
        rrhh_user = self.create_rrhh_user(
            email="rrhh-review-edit-only@example.com",
            dni="11111111H",
        )
        _employee_user, employee = self.create_employee_user(
            email="employee-review-edit-only@example.com",
            dni="13579135G",
        )
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )

        self.client.force_login(rrhh_user)

        response = self.client.post(
            reverse("vacations:review-request", args=[vacation_request.pk]),
            {
                "status": str(self.pending_status.pk),
                "start_date": "2026-07-02",
                "end_date": "2026-07-06",
                "hr_comment": "Solo se ajustan las fechas",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:rrhh-home"))
        vacation_request.refresh_from_db()
        self.assertEqual(vacation_request.status, self.pending_status)
        self.assertEqual(vacation_request.start_date, date(2026, 7, 2))
        self.assertEqual(vacation_request.end_date, date(2026, 7, 6))
        self.assertEqual(Notification.objects.count(), 0)

    def test_rrhh_cannot_open_review_page_for_own_request(self):
        rrhh_user, employee = self.create_rrhh_user_with_employee_profile(
            email="rrhh-own-review-open@example.com",
            dni="56565656P",
        )
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )

        self.client.force_login(rrhh_user)

        response = self.client.get(
            reverse("vacations:review-request", args=[vacation_request.pk]),
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:rrhh-home"))
        self.assertContains(
            response,
            "No puedes revisar tu propia solicitud de vacaciones. Debe gestionarla otro usuario de RRHH.",
        )

    def test_rrhh_cannot_update_own_request(self):
        rrhh_user, employee = self.create_rrhh_user_with_employee_profile(
            email="rrhh-own-review-update@example.com",
            dni="13579135G",
        )
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )

        self.client.force_login(rrhh_user)

        response = self.client.post(
            reverse("vacations:review-request", args=[vacation_request.pk]),
            {
                "status": str(self.approved_status.pk),
                "start_date": "2026-07-10",
                "end_date": "2026-07-12",
                "hr_comment": "Intento de autoaprobacion",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:rrhh-home"))
        vacation_request.refresh_from_db()
        self.assertEqual(vacation_request.status, self.pending_status)
        self.assertEqual(vacation_request.start_date, date(2026, 7, 1))
        self.assertEqual(vacation_request.end_date, date(2026, 7, 5))
        self.assertIsNone(vacation_request.resolved_by)
        self.assertEqual(Notification.objects.count(), 0)

    def test_another_rrhh_user_can_review_request_created_by_rrhh(self):
        owner_rrhh_user, employee = self.create_rrhh_user_with_employee_profile(
            email="rrhh-owner-review@example.com",
            dni="66666666Q",
        )
        reviewer_rrhh_user = self.create_rrhh_user(
            email="rrhh-reviewer@example.com",
            dni="77777777B",
        )
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )

        self.client.force_login(reviewer_rrhh_user)

        response = self.client.post(
            reverse("vacations:review-request", args=[vacation_request.pk]),
            {
                "status": str(self.approved_status.pk),
                "start_date": "2026-07-08",
                "end_date": "2026-07-10",
                "hr_comment": "Aprobada por otro usuario RRHH",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:rrhh-home"))
        vacation_request.refresh_from_db()
        self.assertEqual(vacation_request.status, self.approved_status)
        self.assertEqual(vacation_request.resolved_by, reviewer_rrhh_user)
        self.assertNotEqual(reviewer_rrhh_user, owner_rrhh_user)

        notification = Notification.objects.get(user=owner_rrhh_user)
        self.assertEqual(
            notification.notification_type,
            Notification.Type.VACATION_REQUEST_STATUS,
        )
        self.assertEqual(notification.vacation_request, vacation_request)

    def test_employee_cannot_open_rrhh_review_page(self):
        employee_user, employee = self.create_employee_user(
            email="employee-review-forbidden@example.com",
            dni="33333333P",
        )
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 5),
            requested_days="5.00",
        )

        self.client.force_login(employee_user)

        response = self.client.get(
            reverse("vacations:review-request", args=[vacation_request.pk])
        )

        self.assertRedirects(
            response,
            reverse("dashboard:home"),
            fetch_redirect_response=False,
        )

    def test_admin_can_update_request_and_returns_to_admin_requests_panel(self):
        admin_user = self.create_admin_user(
            email="admin-review-update@example.com",
            dni="56565656P",
        )
        _employee_user, employee = self.create_employee_user(
            email="employee-review-admin-update@example.com",
            dni="78787878K",
        )
        vacation_request = VacationRequest.objects.create(
            employee=employee,
            status=self.pending_status,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            requested_days="5.00",
        )

        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("vacations:review-request", args=[vacation_request.pk]),
            {
                "status": str(self.approved_status.pk),
                "start_date": "2026-07-08",
                "end_date": "2026-07-10",
                "hr_comment": "Aprobada desde administracion",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:admin-requests"))
        vacation_request.refresh_from_db()
        self.assertEqual(vacation_request.status, self.approved_status)
        self.assertEqual(vacation_request.resolved_by, admin_user)
