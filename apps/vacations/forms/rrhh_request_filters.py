"""Formulario GET para filtrar la tabla basica del panel de RRHH."""

from django import forms

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
        label="Nombre o apellido",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": "Buscar empleado",
                "autocomplete": "off",
            }
        ),
    )
    start_date = forms.DateField(
        label="Fecha inicio",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "ui-input ui-input--date ui-input--has-right-icon",
                "type": "date",
            }
        ),
    )
    end_date = forms.DateField(
        label="Fecha final",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "ui-input ui-input--date ui-input--has-right-icon",
                "type": "date",
            }
        ),
    )
    status = forms.ChoiceField(
        label="Estado",
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
        status_choices = [("", "Todos")]
        status_choices.extend(
            (status.name, status.name.capitalize())
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
                "La fecha final del filtro no puede ser anterior a la fecha de inicio."
            )

        return cleaned_data
