"""Formulario basico para crear solicitudes de vacaciones del empleado."""

from django import forms


class VacationRequestForm(forms.Form):
    """Recoge las fechas y el comentario inicial de la solicitud.

    En esta vista la interfaz usa dos calendarios visuales propios en el
    frontend. Por eso las fechas se transportan al backend mediante inputs
    ocultos en formato ISO (`YYYY-MM-DD`), aunque internamente Django las siga
    tratando como `DateField`.

    La validacion del rango se hace aqui para que el usuario reciba un error
    claro antes de entrar en la capa de servicio.
    """

    start_date = forms.DateField(
        label="Fecha de inicio",
        widget=forms.HiddenInput(),
    )
    end_date = forms.DateField(
        label="Fecha de fin",
        widget=forms.HiddenInput(),
    )
    employee_comment = forms.CharField(
        label="Información adicional",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    def clean(self):
        """Evita rangos imposibles como fin anterior al inicio."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                "La fecha de fin no puede ser anterior a la fecha de inicio."
            )

        return cleaned_data
