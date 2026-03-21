"""Configuracion del Django admin para usuarios y roles del sistema."""

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from apps.users.models import Role, User
from apps.users.selectors import get_primary_role


class UserAdminCreationForm(forms.ModelForm):
    """Formulario de alta en admin con un unico rol funcional por usuario."""

    password1 = forms.CharField(label="Contrasena", strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Confirmar contrasena",
        strip=False,
        widget=forms.PasswordInput,
    )
    primary_role = forms.ModelChoiceField(
        queryset=Role.objects.order_by("name"),
        label="Rol principal",
        required=True,
    )

    class Meta:
        model = User
        fields = ("email", "dni", "is_active", "is_staff", "is_superuser")

    def __init__(self, *args, **kwargs):
        """Preselecciona employee para que sea el alta mas natural."""
        super().__init__(*args, **kwargs)
        default_role = Role.objects.filter(name="employee").first()
        if default_role is not None:
            self.fields["primary_role"].initial = default_role

    def clean_password2(self):
        """Comprueba que las dos contrasenas coinciden antes de guardar."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contrasenas no coinciden.")
        return password2

    def save(self, commit=True):
        """Crea el usuario, cifra su contrasena y deja solo un rol asignado."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            user.roles.set([self.cleaned_data["primary_role"]])
        return user


class UserAdminChangeForm(forms.ModelForm):
    """Formulario de edicion que deja visible el rol principal del usuario."""

    password = ReadOnlyPasswordHashField(label="Contrasena")
    primary_role = forms.ModelChoiceField(
        queryset=Role.objects.order_by("name"),
        label="Rol principal",
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "dni",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "activation_token",
            "token_expires_at",
            "registered_at",
        )

    def __init__(self, *args, **kwargs):
        """Carga el rol activo del usuario para editarlo desde una sola lista."""
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            current_role_name = get_primary_role(self.instance)
            if current_role_name:
                current_role = Role.objects.filter(name=current_role_name).first()
                if current_role is not None:
                    self.fields["primary_role"].initial = current_role

    def save(self, commit=True):
        """Actualiza el usuario y reemplaza el rol anterior por el seleccionado."""
        user = super().save(commit=commit)
        if commit:
            user.roles.set([self.cleaned_data["primary_role"]])
        return user


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin del catalogo de roles disponibles en el sistema."""

    list_display = ("name", "description", "users_count")
    search_fields = ("name", "description")
    ordering = ("name",)

    def users_count(self, obj):
        """Muestra cuantos usuarios tienen asociado cada rol."""
        return obj.users.count()

    users_count.short_description = "Usuarios"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin del usuario personalizado con selector de rol principal."""

    add_form = UserAdminCreationForm
    form = UserAdminChangeForm
    model = User
    ordering = ("email",)
    list_display = (
        "email",
        "dni",
        "primary_role_display",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("email", "dni")
    filter_horizontal = ("groups", "user_permissions")
    readonly_fields = (
        "last_login",
        "created_at",
        "updated_at",
        "activation_token",
        "token_expires_at",
        "registered_at",
    )

    fieldsets = (
        (
            "Acceso",
            {
                "fields": ("email", "dni", "password"),
            },
        ),
        (
            "Rol y estado",
            {
                "fields": (
                    "primary_role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (
            "Permisos de Django",
            {
                "fields": ("groups", "user_permissions"),
            },
        ),
        (
            "Datos de activacion",
            {
                "fields": (
                    "activation_token",
                    "token_expires_at",
                    "registered_at",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "fields": ("last_login", "created_at", "updated_at"),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "dni",
                    "password1",
                    "password2",
                    "primary_role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    def primary_role_display(self, obj):
        """Resume en listado el rol funcional que ve el sistema."""
        return get_primary_role(obj) or "Sin rol"

    primary_role_display.short_description = "Rol"
