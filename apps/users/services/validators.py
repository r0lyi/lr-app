import re

from django.core.exceptions import ValidationError


DNI_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"
DNI_RE = re.compile(r"^\d{8}[A-Z]$")


def normalize_dni(value: str) -> str:
    if value is None:
        return value
    return re.sub(r"[\s-]+", "", value).upper()


def validate_dni(value: str) -> None:
    if not value:
        raise ValidationError("El DNI es obligatorio.")

    normalized = normalize_dni(value)
    if not DNI_RE.match(normalized):
        raise ValidationError("El DNI debe tener 8 numeros y una letra.")

    number = int(normalized[:8])
    expected_letter = DNI_LETTERS[number % 23]
    if normalized[-1] != expected_letter:
        raise ValidationError("El DNI no es valido.")
