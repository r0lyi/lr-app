"""Servicios administrativos del dominio users.

Estas funciones encapsulan acciones de gestion sobre usuarios que el panel
admin puede disparar sin mover reglas de negocio al dashboard.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.employees.models import Employee
from apps.users.models import User
from apps.users.services.auth_service import request_activation
from apps.users.services.validators import normalize_dni

ROLE_LABELS = {
    "employee": _("Empleado"),
    "rrhh": _("RRHH"),
    "admin": _("Administrador"),
}


def _get_user_primary_role_name(user):
    """Devuelve el rol funcional actual del usuario antes del cambio."""

    role_names = list(user.roles.values_list("name", flat=True))
    for role_name in ("admin", "rrhh", "employee"):
        if role_name in role_names:
            return role_name
    return None


def change_user_primary_role(*, acting_user, target_user, new_role):
    """Reemplaza el rol principal de un usuario por uno nuevo.

    Reglas de seguridad aplicadas:
    - solo se permite gestionar usuarios no superusuario desde el panel
    - no se puede quitar el rol admin al ultimo admin funcional del sistema

    El proyecto trabaja por ahora con un unico rol practico por usuario, asi
    que la actualizacion usa ``set([new_role])`` en lugar de acumular roles.
    """

    if target_user.is_superuser:
        raise ValidationError(
            _("Los superusuarios se gestionan desde Django admin."),
        )

    previous_role_name = _get_user_primary_role_name(target_user)
    current_role_names = set(
        target_user.roles.values_list("name", flat=True)
    )
    if "admin" in current_role_names and new_role.name != "admin":
        admin_users_count = User.objects.filter(roles__name="admin").distinct().count()
        if admin_users_count <= 1:
            raise ValidationError(
                _("No puedes quitar el rol admin al ultimo administrador del sistema."),
            )

    target_user.roles.set([new_role])

    # Registramos el cambio con un texto legible en el dominio de auditoria.
    # El import se deja aqui para evitar dependencias circulares durante la
    # carga inicial de apps y modelos.
    if previous_role_name != new_role.name:
        from apps.audit.services import log_user_primary_role_changed

        log_user_primary_role_changed(
            acting_user=acting_user,
            target_user=target_user,
            previous_role_name=previous_role_name,
            new_role_name=new_role.name,
        )

    return target_user


def change_user_active_state(*, acting_user, target_user, is_active):
    """Activa o desactiva una cuenta desde el panel admin.

    Reglas aplicadas:
    - los superusuarios solo se gestionan desde Django admin
    - no se puede desactivar al ultimo admin activo del sistema
    - no se puede activar manualmente una cuenta sin contraseña usable

    Esto evita estados confusos para el equipo gestor y protege el acceso
    administrativo minimo necesario para mantener la aplicacion operativa.
    """

    if target_user.is_superuser:
        raise ValidationError(
            _("Los superusuarios se gestionan desde Django admin."),
        )

    if target_user.is_active == is_active:
        return target_user

    current_role_names = set(target_user.roles.values_list("name", flat=True))
    if "admin" in current_role_names and target_user.is_active and not is_active:
        remaining_active_admins = (
            User.objects.filter(is_active=True, roles__name="admin")
            .exclude(pk=target_user.pk)
            .distinct()
            .count()
        )
        if remaining_active_admins <= 0:
            raise ValidationError(
                _(
                    "No puedes desactivar al ultimo administrador activo del sistema."
                ),
            )

    if is_active and not target_user.has_usable_password():
        raise ValidationError(
            _(
                "Esta cuenta aun no tiene una contrasena configurada. "
                "Primero debe completar su acceso desde el enlace de activacion."
            ),
        )

    target_user.is_active = is_active
    target_user.save(update_fields=["is_active"])

    from apps.audit.services import log_user_access_state_changed

    log_user_access_state_changed(
        acting_user=acting_user,
        target_user=target_user,
        is_active=is_active,
    )

    return target_user


def change_user_department(*, acting_user, target_user, new_department):
    """Actualiza el departamento de la ficha Employee desde el panel admin.

    Esta accion se ofrece dentro de la gestion de usuarios porque el objetivo
    del proyecto es centralizar en el panel admin los cambios administrativos
    mas habituales. Aun asi, la logica sigue viviendo en el dominio ``users``
    para que la vista solo orqueste formulario y mensajes.
    """

    try:
        employee_profile = target_user.employee_profile
    except Employee.DoesNotExist as exc:
        raise ValidationError(
            _(
                "Este usuario aun no tiene ficha de empleado. "
                "Primero debe completar su registro interno."
            ),
        ) from exc

    previous_department_name = (
        employee_profile.department.name if employee_profile.department else None
    )
    new_department_name = new_department.name if new_department else None

    if previous_department_name == new_department_name:
        return target_user

    employee_profile.department = new_department
    employee_profile.save(update_fields=["department"])

    from apps.audit.services import log_user_department_changed

    log_user_department_changed(
        acting_user=acting_user,
        target_user=target_user,
        previous_department_name=previous_department_name,
        new_department_name=new_department_name,
    )

    return target_user


def create_admin_user(*, acting_user, email, dni, activation_url_base=None):
    """Crea una cuenta pendiente de activacion con DNI y correo electronico.

    El usuario queda inactivo y recibe automaticamente un enlace de activacion
    para que complete su acceso sin que el admin tenga que abandonar el panel.
    """

    normalized_email = (email or "").strip().lower()
    normalized_dni = normalize_dni(dni)

    if User.objects.filter(dni=normalized_dni).exists():
        raise ValidationError({"dni": _("Ya existe un usuario con este DNI.")})

    if User.objects.filter(email__iexact=normalized_email).exists():
        raise ValidationError(
            {"email": _("Ya existe un usuario con este correo electrónico.")}
        )

    with transaction.atomic():
        user = User.objects.create_user(
            email=normalized_email,
            dni=normalized_dni,
        )
        sent, _ = request_activation(
            user.dni,
            activation_url_base=activation_url_base,
        )
        if not sent:
            raise ValidationError(
                _("No se pudo generar el enlace de activacion para el nuevo usuario.")
            )

        from apps.audit.services import log_user_created

        log_user_created(
            acting_user=acting_user,
            target_user=user,
        )

    return user
