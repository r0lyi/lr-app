"""Formulario GET para filtrar la tabla basica del panel de RRHH."""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.vacations.models import VacationStatus


class RrhhVacationRequestFilterForm(forms.Form):
    """Recoge filtros simples para la lista de solicitudes visible en RRHH.

    En esta primera version permitimos:
    - buscar por nombre o apellido del empleado
    - limitar por fecha de inicio minima
    - limitar por fecha final maxima
    - limitar por estado concreto
    """

    search = forms.CharField(
        label=_("Empleado"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": _("Buscar por nombre..."),
                "autocomplete": "off",
            }
        ),
    )
    start_date = forms.DateField(
        label=_("Fecha inicio"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "ui-input ui-input--date ui-input--has-right-icon",
                "type": "date",
            }
        ),
    )
    end_date = forms.DateField(
        label=_("Fecha final"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "ui-input ui-input--date ui-input--has-right-icon",
                "type": "date",
            }
        ),
    )
    status = forms.ChoiceField(
        label=_("Estado"),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "ui-select",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        """Carga los estados reales de BD para no hardcodear el filtro."""

        super().__init__(*args, **kwargs)
        status_choices = [("", _("Todos los estados"))]
        status_choices.extend(
            (status.name, str(status))
            for status in VacationStatus.objects.order_by("name")
        )
        self.fields["status"].choices = status_choices

    def clean(self):
        """Evita rangos incoherentes donde la fecha final sea anterior."""

        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                _(
                    "La fecha final del filtro no puede ser anterior a la fecha de inicio."
                )
            )

        return cleaned_data
