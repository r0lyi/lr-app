"""Tests de presentacion para el shell de dashboard."""

from datetime import date

from django.test import TestCase

from apps.core.presentation.dashboard.context import build_dashboard_base_context
from apps.core.presentation.dashboard.display import (
    AVATAR_THEMES,
    get_dashboard_avatar_theme,
    get_dashboard_display_initials,
)
from apps.employees.models import Employee
from apps.users.models import User


class DashboardDisplayTests(TestCase):
    """Verifica los datos visibles que alimentan el header del dashboard."""

    def test_display_initials_use_first_name_and_last_name(self):
        user = User.objects.create_user(
            email="rosa.sanchez@example.com",
            dni="12345678Z",
            password="PruebaSegura123!",
            is_active=True,
        )
        Employee.objects.create(
            user=user,
            first_name="Rosa",
            last_name="Sanchez",
            phone="600123123",
            hire_date=date(2024, 1, 15),
        )

        self.assertEqual(get_dashboard_display_initials(user), "RS")

    def test_avatar_theme_is_stable_and_uses_the_palette(self):
        user = User.objects.create_user(
            email="carlos.martinez@example.com",
            dni="87654321X",
            password="PruebaSegura123!",
            is_active=True,
        )

        theme_one = get_dashboard_avatar_theme(user)
        theme_two = get_dashboard_avatar_theme(user)

        self.assertEqual(theme_one, theme_two)
        self.assertIn(theme_one, AVATAR_THEMES)

    def test_dashboard_context_includes_avatar_theme(self):
        user = User.objects.create_user(
            email="ana.perez@example.com",
            dni="12345678Z",
            password="PruebaSegura123!",
            is_active=True,
        )

        context = build_dashboard_base_context(user, "employee")

        self.assertIn("display_avatar_background", context)
        self.assertIn("display_avatar_foreground", context)
        self.assertIn(context["display_avatar_background"], [theme["background"] for theme in AVATAR_THEMES])
        self.assertIn(context["display_avatar_foreground"], [theme["foreground"] for theme in AVATAR_THEMES])
