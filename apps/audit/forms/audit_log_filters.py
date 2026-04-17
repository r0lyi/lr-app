"""Formulario GET para encontrar actividad concreta dentro del historial."""

from django import forms

from apps.audit.models import AuditLog
from apps.audit.services import (
    AUDIT_ACTION_USER_ACCESS_STATE_CHANGED,
    AUDIT_ACTION_USER_ACCOUNT_ACTIVATED,
    AUDIT_ACTION_USER_CREATED,
    AUDIT_ACTION_USER_PASSWORD_CHANGED,
    AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED,
    AUDIT_ACTION_USER_PROFILE_UPDATED,
    AUDIT_ACTION_VACATION_REQUEST_REVIEWED,
)


VISIBLE_AUDIT_ACTION_CHOICES = (
    ("", "Todos"),
    (AUDIT_ACTION_USER_CREATED, "Usuario creado"),
    (AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED, "Cambio de rol"),
    (AUDIT_ACTION_USER_ACCESS_STATE_CHANGED, "Cambio de acceso"),
    (AUDIT_ACTION_USER_PROFILE_UPDATED, "Datos de usuario"),
    (AUDIT_ACTION_USER_PASSWORD_CHANGED, "Contraseña actualizada"),
    (AUDIT_ACTION_USER_ACCOUNT_ACTIVATED, "Cuenta activada"),
    (AUDIT_ACTION_VACATION_REQUEST_REVIEWED, "Solicitud editada"),
)
VISIBLE_AUDIT_ACTIONS = {
    action
    for action, _label in VISIBLE_AUDIT_ACTION_CHOICES
    if action
}


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
                "placeholder": "Ej. usuario, solicitud o cambio...",
            }
        ),
    )
    action = forms.ChoiceField(
        required=False,
        label="Tipo de cambio",
        choices=VISIBLE_AUDIT_ACTION_CHOICES,
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
        if action and (
            action not in AuditLog.ACTION_LABELS
            or action not in VISIBLE_AUDIT_ACTIONS
        ):
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
