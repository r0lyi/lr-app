"""Formularios del onboarding interno de empleados."""

from django import forms
from django.core.exceptions import ValidationError

from apps.users.models import User


class EmployeeOnboardingForm(forms.Form):
    """Captura los datos minimos para crear o completar la ficha `Employee`."""

    first_name = forms.CharField(
        max_length=100,
        label="Nombre",
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": "Introduce tu nombre",
                "autocomplete": "given-name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=100,
        label="Apellidos",
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": "Introduce tus apellidos",
                "autocomplete": "family-name",
            }
        ),
    )
    email = forms.EmailField(
        label="Correo electronico",
        widget=forms.EmailInput(
            attrs={
                "class": "ui-input",
                "placeholder": "Introduce tu correo",
                "autocomplete": "email",
            }
        ),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Telefono",
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": "Introduce tu telefono",
                "autocomplete": "tel",
            }
        ),
    )
    hire_date = forms.DateField(
        label="Fecha de ingreso",
        widget=forms.DateInput(
            attrs={
                "class": "ui-input",
                "type": "date",
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs):
        """Recibe el usuario actual para excluirlo de la validacion de email."""

        self.user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        """Impide reutilizar el email de otro usuario del sistema."""

        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise ValidationError("Este correo ya esta en uso.")
        return email
