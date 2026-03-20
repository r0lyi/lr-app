from django import forms
from django.contrib.auth.password_validation import validate_password
from apps.users.services.validators import normalize_dni, validate_dni

# Formulario para solicitar activación de cuenta mediante DNI
class RequestActivationForm(forms.Form):
    dni = forms.CharField(
        max_length=20,
        validators=[validate_dni],
        widget=forms.TextInput(attrs={
            "placeholder": "Introduce tu DNI",
            "class": "input",
            "autofocus": True,
        })
    )

    def clean_dni(self):
        return normalize_dni(self.cleaned_data["dni"])

# Formulario para establecer nueva contraseña después de activar cuenta
class SetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={"class": "input"}),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "input"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

# Formulario de login usando DNI y contraseña
class LoginForm(forms.Form):
    dni = forms.CharField(
        max_length=20,
        validators=[validate_dni],
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "DNI"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Contraseña"}),
    )

    def clean_dni(self):
        return normalize_dni(self.cleaned_data["dni"])
