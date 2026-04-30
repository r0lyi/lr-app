"""Formulario GET para filtrar las solicitudes visibles en el home del empleado."""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.vacations.models import VacationStatus


class EmployeeVacationRequestFilterForm(forms.Form):
    """Recoge filtros simples para acotar la lista de solicitudes.

    En esta primera version permitimos tres criterios:
    - fecha de inicio minima del rango solicitado
    - fecha de fin maxima del rango solicitado
    - estado concreto de la solicitud

    El formulario es de tipo GET porque no modifica datos; solo cambia la
    consulta mostrada en pantalla.
    """

    start_date = forms.DateField(
        label=_("Fecha inicio"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "ui-input ui-input--date",
            }
        ),
    )
    end_date = forms.DateField(
        label=_("Fecha final"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "ui-input ui-input--date",
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
        """Carga los estados reales de BD para que el filtro no quede hardcodeado."""
        super().__init__(*args, **kwargs)
        status_choices = [("", _("Todos"))]
        status_choices.extend(
            (status.name, str(status))
            for status in VacationStatus.objects.order_by("name")
        )
        self.fields["status"].choices = status_choices

    def clean(self):
        """Evita filtros incoherentes donde el fin sea anterior al inicio."""
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
