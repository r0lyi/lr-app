"""Formularios del dominio notifications."""

from django import forms
from django.utils.translation import gettext_lazy as _


class AdminPersonalNotificationForm(forms.Form):
    """Recoge un mensaje personal que un admin quiere enviar a un usuario."""

    title = forms.CharField(
        label=_("Asunto"),
        max_length=140,
        error_messages={"required": _("Este campo es obligatorio.")},
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": _("Ej. Recordatorio importante"),
            }
        ),
    )
    message = forms.CharField(
        label=_("Mensaje"),
        error_messages={"required": _("Este campo es obligatorio.")},
        widget=forms.Textarea(
            attrs={
                "class": "ui-input ui-input--textarea",
                "placeholder": _("Escribe aqui el mensaje que recibira el usuario."),
                "rows": 5,
            }
        ),
    )

    def clean_title(self):
        """Elimina espacios sobrantes y evita asuntos vacíos."""

        return (self.cleaned_data["title"] or "").strip()

    def clean_message(self):
        """Normaliza el mensaje antes de enviarlo al inbox interno."""

        return (self.cleaned_data["message"] or "").strip()


class AdminBroadcastNotificationForm(forms.Form):
    """Recoge un aviso general que el admin enviará a todos los usuarios."""

    title = forms.CharField(
        label=_("Asunto general"),
        max_length=140,
        error_messages={"required": _("Este campo es obligatorio.")},
        widget=forms.TextInput(
            attrs={
                "class": "ui-input",
                "placeholder": _("Ej. Aviso general para toda la plantilla"),
            }
        ),
    )
    message = forms.CharField(
        label=_("Mensaje general"),
        error_messages={"required": _("Este campo es obligatorio.")},
        widget=forms.Textarea(
            attrs={
                "class": "ui-input ui-input--textarea",
                "placeholder": _(
                    "Escribe aqui el aviso que recibirán todos los usuarios."
                ),
                "rows": 5,
            }
        ),
    )

    def clean_title(self):
        """Limpia el asunto antes de persistir el aviso general."""

        return (self.cleaned_data["title"] or "").strip()

    def clean_message(self):
        """Normaliza el cuerpo del mensaje global."""

        return (self.cleaned_data["message"] or "").strip()
