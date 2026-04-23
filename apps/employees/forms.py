"""Formularios del onboarding interno de empleados."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.employees.models import Employee
from apps.users.models import User


class EmployeeOnboardingForm(forms.Form):
    """Captura los datos minimos para crear o completar la ficha `Employee`."""

    first_name = forms.CharField(
        max_length=100,
        label=_("Nombre"),
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": _("Introduce tu nombre"),
                "autocomplete": "given-name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=100,
        label=_("Apellidos"),
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": _("Introduce tus apellidos"),
                "autocomplete": "family-name",
            }
        ),
    )
    email = forms.EmailField(
        label=_("Correo electrónico"),
        widget=forms.EmailInput(
            attrs={
                "class": "ui-input",
                "placeholder": _("Introduce tu correo"),
                "autocomplete": "email",
            }
        ),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label=_("Teléfono"),
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": _("Introduce tu teléfono"),
                "autocomplete": "tel",
            }
        ),
    )
    hire_date = forms.DateField(
        label=_("Fecha de ingreso"),
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
            raise ValidationError(_("Este correo ya está en uso."))
        return email


class EmployeeProfileUpdateForm(forms.ModelForm):
    """Permite editar la ficha del empleado sin tocar correo ni fecha de ingreso.

    La regla actual del perfil es deliberadamente conservadora: el usuario solo
    puede corregir sus datos personales mas inmediatos. El resto de campos del
    modelo `Employee` se muestran en modo lectura para evitar que datos de RRHH
    o acumulados internos se alteren desde esta pantalla.
    """

    class Meta:
        model = Employee
        fields = (
            "first_name",
            "last_name",
            "phone",
        )
        labels = {
            "first_name": _("Nombre"),
            "last_name": _("Apellidos"),
            "phone": _("Teléfono"),
        }
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "ui-input",
                    "autocomplete": "given-name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "ui-input",
                    "autocomplete": "family-name",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "ui-input",
                    "autocomplete": "tel",
                }
            ),
        }
