"""Modelo de usuario personalizado y relacion con roles de aplicacion."""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.core.models import TimeStampedModel

from .role import Role
from apps.users.services.validators import normalize_dni, validate_dni

# Todo usuario nuevo nace como employee salvo que se le cambie despues.
DEFAULT_ROLE_NAME = "employee"


class UserManager(BaseUserManager):
    """Manager para crear usuarios usando email + DNI como datos base."""

    def create_user(self, email, dni, password=None, **extra_fields):
        """Crea un usuario normal validando y normalizando el DNI."""
        if not email:
            raise ValueError("El email es obligatorio")
        if not dni:
            raise ValueError("El DNI es obligatorio")

        email = self.normalize_email(email)
        dni = normalize_dni(dni)
        validate_dni(dni)
        user  = self.model(email=email, dni=dni, **extra_fields)

        if password:
            user.set_password(password)
        else:
            # Force unusable password for activation-flow users.
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, dni, password=None, **extra_fields):
        """Crea un superusuario con permisos completos de Django."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not password:
            raise ValueError("El superusuario debe tener contraseña.")
        return self.create_user(email, dni, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Usuario principal del sistema con activacion por token y roles propios."""

    email = models.EmailField(max_length=150, unique=True)
    dni = models.CharField(max_length=20, unique=True, validators=[validate_dni])
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=255, blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    registered_at = models.DateTimeField(blank=True, null=True)

    roles = models.ManyToManyField(
        Role,
        through="UserRole",
        related_name="users",
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["dni"]

    class Meta:
        db_table = "users"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Guarda el usuario y le asigna employee por defecto al crearse."""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # El catalogo de roles ya debe existir por migracion.
            try:
                default_role = Role.objects.get(name=DEFAULT_ROLE_NAME)
            except Role.DoesNotExist:
                default_role = None

            if default_role is not None:
                self.roles.add(default_role)


class UserRole(models.Model):
    """Tabla intermedia para relacionar usuarios con multiples roles."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        db_table = "user_role"
        unique_together = ("user", "role")
        verbose_name = "Rol de usuario"
