"""Helpers de presentacion para encabezados y datos visibles del dashboard."""

from __future__ import annotations

import hashlib
import re

from apps.employees.models import Employee

AVATAR_THEMES = (
    {"background": "#F5F2B8", "foreground": "#D68818"},
    {"background": "#E2F0D9", "foreground": "#2E8B57"},
    {"background": "#E3F1FF", "foreground": "#2D7CC1"},
    {"background": "#F3E3D6", "foreground": "#C46A23"},
    {"background": "#E9E1FF", "foreground": "#7A57C5"},
    {"background": "#E1F7F2", "foreground": "#1E9A7A"},
    {"background": "#FCE6E7", "foreground": "#C15A67"},
    {"background": "#F3EBDD", "foreground": "#B88D2C"},
)


def get_dashboard_display_name(user):
    """Devuelve un nombre legible para el encabezado del dashboard."""

    try:
        profile = user.employee_profile
    except Employee.DoesNotExist:
        profile = None

    if profile is not None:
        full_name = f"{profile.first_name} {profile.last_name}".strip()
        if full_name:
            return full_name

    email = (user.email or "").strip()
    if "@" in email:
        return email.split("@", 1)[0]
    return email or "Usuario"


def get_dashboard_display_initials(user):
    """Devuelve unas iniciales cortas para el avatar del dashboard."""

    try:
        profile = user.employee_profile
    except Employee.DoesNotExist:
        profile = None

    if profile is not None:
        full_name = f"{profile.first_name} {profile.last_name}".strip()
        if full_name:
            parts = [part for part in full_name.split() if part]
            initials = "".join(part[0] for part in parts[:2]).upper()
            if initials:
                return initials

    email = (user.email or "").strip()
    if email:
        local_part = email.split("@", 1)[0]
        chunks = [chunk for chunk in re.split(r"[._-]+", local_part) if chunk]
        initials = "".join(chunk[0] for chunk in chunks[:2]).upper()
        if initials:
            return initials

    return "U"


def get_dashboard_avatar_theme(user):
    """Devuelve un color pastel estable para el avatar de iniciales."""

    seed = str(getattr(user, "pk", "") or "").strip()
    if not seed:
        email = (getattr(user, "email", "") or "").strip()
        if email:
            seed = email
        else:
            seed = get_dashboard_display_name(user)

    digest = hashlib.blake2s(seed.encode("utf-8"), digest_size=2).digest()
    index = int.from_bytes(digest, "big") % len(AVATAR_THEMES)
    return AVATAR_THEMES[index]
