"""Formularios del flujo de activacion y login por DNI."""

from django import forms
from django.contrib.auth.password_validation import validate_password

from apps.users.services.validators import normalize_dni, validate_dni


class RequestActivationForm(forms.Form):
    """Solicita el enlace de activacion o recuperacion a partir del DNI."""

    dni = forms.CharField(
        max_length=20,
        validators=[validate_dni],
        widget=forms.TextInput(attrs={
            "placeholder": "Introduce tu DNI",
            "class": "input",
            "autofocus": True,
        })
    )

    def clean_dni(self):
        """Normaliza el DNI antes de pasarlo al servicio de activacion."""

        return normalize_dni(self.cleaned_data["dni"])


class SetPasswordForm(forms.Form):
    """Permite definir la contraseña desde un token valido de activacion."""

    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={"class": "input"}),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "input"}),
    )

    def clean(self):
        """Comprueba que ambas contraseñas coinciden antes de guardar."""

        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data


class LoginForm(forms.Form):
    """Recoge las credenciales del login basado en DNI."""

    dni = forms.CharField(
        max_length=20,
        validators=[validate_dni],
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "DNI"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Contraseña"}),
    )

    def clean_dni(self):
        """Aplica la misma normalizacion del DNI usada en el resto del flujo."""

        return normalize_dni(self.cleaned_data["dni"])
