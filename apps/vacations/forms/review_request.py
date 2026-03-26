"""Formulario minimo para que RRHH revise una solicitud existente."""

from django import forms

from apps.vacations.models import VacationStatus


class VacationRequestReviewForm(forms.Form):
    """Permite a RRHH ajustar estado, fechas y comentario interno.

    En esta primera fase mantenemos el formulario pequeño y centrado en las dos
    acciones pedidas:
    - cambiar el estado de la solicitud
    - corregir el rango de fechas si hace falta
    """

    status = forms.ModelChoiceField(
        label="Estado",
        queryset=VacationStatus.objects.order_by("name"),
        empty_label=None,
        widget=forms.Select(
            attrs={
                "class": "ui-select",
            }
        ),
    )
    start_date = forms.DateField(
        label="Fecha inicio",
        widget=forms.DateInput(
            attrs={
                "class": "ui-input ui-input--date ui-input--has-right-icon",
                "type": "date",
            }
        ),
    )
    end_date = forms.DateField(
        label="Fecha final",
        widget=forms.DateInput(
            attrs={
                "class": "ui-input ui-input--date ui-input--has-right-icon",
                "type": "date",
            }
        ),
    )
    hr_comment = forms.CharField(
        label="Comentario RRHH",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "ui-input ui-input--textarea",
                "rows": 4,
                "placeholder": "Escribe una observacion interna si necesitas dejar contexto sobre el cambio realizado.",
            }
        ),
    )

    def clean(self):
        """Evita enviar un rango de fechas invertido desde RRHH."""

        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                "La fecha final no puede ser anterior a la fecha de inicio."
            )

        return cleaned_data
