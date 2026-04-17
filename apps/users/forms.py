"""Formularios del flujo de activacion, login y gestion basica de usuarios."""

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX

from apps.users.models import User

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
        """Normaliza el DNI pero exige que la letra ya venga en mayusculas."""

        raw_dni = self.data.get(self.add_prefix("dni"), self.data.get("dni", ""))
        compact_dni = "".join(ch for ch in str(raw_dni) if ch not in {" ", "-"})
        normalized_dni = normalize_dni(self.cleaned_data["dni"])

        if compact_dni and compact_dni != normalized_dni and compact_dni.upper() == normalized_dni:
            raise forms.ValidationError("La letra del DNI debe escribirse en mayúsculas.")

        return normalized_dni


class AdminUserFilterForm(forms.Form):
    """Recoge filtros simples para hacer mas util el listado administrativo.

    La pantalla de usuarios la usan personas que necesitan localizar cuentas
    con rapidez, asi que este formulario prioriza criterios muy directos:
    nombre o correo, rol principal y estado de acceso.
    """

    ACCESS_STATE_ACTIVE = "active"
    ACCESS_STATE_INACTIVE = "inactive"
    ACCESS_STATE_PENDING = "pending_activation"

    search = forms.CharField(
        required=False,
        label="Buscar usuario",
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": "Buscar por nombre, email o ID...",
            }
        ),
    )
    primary_role = forms.ChoiceField(
        required=False,
        label="Rol",
        choices=(
            ("", "Todos los roles"),
            ("employee", "Empleado"),
            ("rrhh", "RRHH"),
            ("admin", "Administrador"),
        ),
        widget=forms.Select(attrs={"class": "ui-select"}),
    )
    access_state = forms.ChoiceField(
        required=False,
        label="Acceso",
        choices=(
            ("", "Todos los estados"),
            (ACCESS_STATE_ACTIVE, "Acceso activo"),
            (ACCESS_STATE_INACTIVE, "Acceso desactivado"),
            (ACCESS_STATE_PENDING, "Pendiente de activar"),
        ),
        widget=forms.Select(attrs={"class": "ui-select"}),
    )


class AdminUserCreateForm(forms.Form):
    """Formulario corto para crear un usuario pendiente de activacion desde admin."""

    dni = forms.CharField(
        max_length=20,
        label="DNI",
        validators=[validate_dni],
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": "12345678Z",
                "autofocus": True,
            }
        ),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": "nombre@empresa.com",
                "inputmode": "email",
            }
        ),
    )

    def clean_dni(self):
        """Normaliza el DNI antes de validar la unicidad."""

        return normalize_dni(self.cleaned_data["dni"])

    def clean_email(self):
        """Normaliza el email para evitar duplicados por mayusculas o espacios."""

        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        """Comprueba que no exista ya un usuario con esos identificadores."""

        cleaned_data = super().clean()
        dni = cleaned_data.get("dni")
        email = cleaned_data.get("email")

        if dni and User.objects.filter(dni=dni).exists():
            self.add_error("dni", "Ya existe un usuario con este DNI.")

        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error("email", "Ya existe un usuario con este correo electrónico.")

        return cleaned_data


__all__ = [
    "AdminUserFilterForm",
    "AdminUserCreateForm",
    "LoginForm",
    "RequestActivationForm",
    "SetPasswordForm",
    "UNUSABLE_PASSWORD_PREFIX",
]
