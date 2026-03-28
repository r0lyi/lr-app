"""Servicios administrativos del dominio users.

Estas funciones encapsulan acciones de gestion sobre usuarios que el panel
admin puede disparar sin mover reglas de negocio al dashboard.
"""

from django.core.exceptions import ValidationError

from apps.users.models import User

ROLE_LABELS = {
    "employee": "Empleado",
    "rrhh": "RRHH",
    "admin": "Administrador",
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
            "Los superusuarios se gestionan desde Django admin.",
        )

    previous_role_name = _get_user_primary_role_name(target_user)
    current_role_names = set(
        target_user.roles.values_list("name", flat=True)
    )
    if "admin" in current_role_names and new_role.name != "admin":
        admin_users_count = User.objects.filter(roles__name="admin").distinct().count()
        if admin_users_count <= 1:
            raise ValidationError(
                "No puedes quitar el rol admin al ultimo administrador del sistema.",
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
