"""Formulario GET para filtrar el historial de exportaciones."""

from django import forms
from django.utils.translation import gettext_lazy as _


class ExportHistoryFilterForm(forms.Form):
    """Permite acotar el historial por un rango de fechas de creacion."""

    start_date = forms.DateField(
        required=False,
        label=_("Fecha inicio"),
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "ui-input ui-input--date",
            }
        ),
    )
    end_date = forms.DateField(
        required=False,
        label=_("Fecha final"),
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "ui-input ui-input--date",
            }
        ),
    )

    def clean(self):
        """Evita enviar un rango de fechas invertido."""

        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                _("La fecha final no puede ser anterior a la fecha inicial.")
            )

        return cleaned_data
