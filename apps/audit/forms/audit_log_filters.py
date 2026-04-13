"""Formulario GET para encontrar actividad concreta dentro del historial."""

from django import forms

from apps.audit.models import AuditLog


class AuditLogFilterForm(forms.Form):
    """Ayuda a localizar actividad por fecha o por lo que ocurrió.

    El objetivo es que el personal administrativo pueda acotar rápido:
    quién hizo algo, qué pasó y en qué periodo ocurrió.
    """

    search = forms.CharField(
        required=False,
        label="Buscar actividad",
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": "Buscar por usuario o por lo que sucedió",
            }
        ),
    )
    action = forms.ChoiceField(
        required=False,
        label="Tipo de cambio",
        choices=(
            ("", "Todas las actividades"),
            ("user_primary_role_changed", "Cambio de rol"),
            ("user_access_state_changed", "Cambio de acceso"),
            ("user_department_changed", "Cambio de departamento"),
        ),
        widget=forms.Select(attrs={"class": "ui-select"}),
    )
    start_date = forms.DateField(
        required=False,
        label="Fecha inicio",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "ui-input ui-input--date",
            }
        ),
    )
    end_date = forms.DateField(
        required=False,
        label="Fecha final",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "ui-input ui-input--date",
            }
        ),
    )

    def clean_action(self):
        """Acepta solo acciones que el historial actual sabe mostrar bien."""

        action = (self.cleaned_data.get("action") or "").strip()
        if action and action not in AuditLog.ACTION_LABELS:
            raise forms.ValidationError("Selecciona un tipo de actividad válido.")
        return action

    def clean(self):
        """Evita rangos de fecha invertidos en el buscador de actividad."""

        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                "La fecha final no puede ser anterior a la fecha inicial."
            )

        return cleaned_data
