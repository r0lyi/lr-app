"""Validadores y normalizadores compartidos del DNI de acceso."""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


DNI_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"
DNI_RE = re.compile(r"^\d{8}[A-Z]$")


def normalize_dni(value: str) -> str:
    """Elimina separadores y fuerza mayusculas para usar un formato unico."""

    if value is None:
        return value
    return re.sub(r"[\s-]+", "", value).upper()


def validate_dni(value: str) -> None:
    """Comprueba formato y letra de control del DNI espanol."""

    if not value:
        raise ValidationError(_("El DNI es obligatorio."))

    normalized = normalize_dni(value)
    if not DNI_RE.match(normalized):
        raise ValidationError(_("El DNI debe tener 8 numeros y una letra."))

    number = int(normalized[:8])
    expected_letter = DNI_LETTERS[number % 23]
    if normalized[-1] != expected_letter:
        raise ValidationError(_("El DNI no es valido."))
