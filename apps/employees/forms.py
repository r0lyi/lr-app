"""Formularios del onboarding interno de empleados."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.employees.models import Employee
from apps.users.models import User


EMPLOYEE_REQUIRED_FIELDS_MESSAGE = _(
    "Debes completar todos los campos obligatorios de la ficha de empleado."
)


def _has_missing_required_fields(form):
    """Indica si el formulario tiene errores por campos obligatorios vacíos."""

    return any(
        any(error.code == "required" for error in errors)
        for field_name, errors in form.errors.as_data().items()
        if field_name != "__all__"
    )


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

    def clean(self):
        """Añade un aviso global cuando faltan campos obligatorios."""

        cleaned_data = super().clean()
        if _has_missing_required_fields(self):
            raise ValidationError(EMPLOYEE_REQUIRED_FIELDS_MESSAGE)
        return cleaned_data


class EmployeeProfileUpdateForm(forms.ModelForm):
    """Permite editar la ficha del empleado sin tocar correo ni fecha de ingreso.

    La regla actual del perfil es deliberadamente conservadora: el usuario solo
    puede corregir sus datos personales mas inmediatos. El resto de campos del
    modelo `Employee` se muestran en modo lectura para evitar que datos de RRHH
    o acumulados internos se alteren desde esta pantalla.
    """

    phone = forms.CharField(
        max_length=20,
        required=True,
        label=_("Teléfono"),
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "autocomplete": "tel",
            }
        ),
    )

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

    def clean(self):
        """Añade un aviso global cuando faltan campos obligatorios."""

        cleaned_data = super().clean()
        if _has_missing_required_fields(self):
            raise ValidationError(EMPLOYEE_REQUIRED_FIELDS_MESSAGE)
        return cleaned_data
