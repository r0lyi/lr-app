"""Servicios para registrar eventos legibles en el historial de auditoria."""

from apps.audit.models import AuditLog

AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED = "user_primary_role_changed"
AUDIT_RESOURCE_TYPE_USER = "user"

ROLE_LABELS = {
    "employee": "Empleado",
    "rrhh": "RRHH",
    "admin": "Administrador",
}


def create_audit_log(*, user, action, resource_type, resource_id, description):
    """Crea un registro de auditoria simple y reutilizable.

    El modelo `AuditLog` es deliberadamente pequeno, asi que centralizamos aqui
    la escritura para que otras apps no necesiten conocer detalles del esquema.
    """

    return AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
    )


def get_role_label(role_name):
    """Traduce el nombre interno del rol a un texto facil de entender."""

    return ROLE_LABELS.get((role_name or "").strip().lower(), "Sin rol")


def build_user_role_change_description(
    *,
    acting_user,
    target_user,
    previous_role_name,
    new_role_name,
):
    """Construye un mensaje de auditoria claro y no tecnico.

    El texto evita jerga innecesaria para que el historial sea facil de leer
    por personas no tecnicas. En lugar de mostrar codigos internos, usamos
    etiquetas como "Empleado" o "Administrador".
    """

    actor_email = (acting_user.email or "").strip()
    target_email = (target_user.email or "").strip()
    previous_role_label = get_role_label(previous_role_name)
    new_role_label = get_role_label(new_role_name)

    return (
        f"{actor_email} cambió el rol principal de {target_email} "
        f"de {previous_role_label} a {new_role_label}."
    )


def log_user_primary_role_changed(
    *,
    acting_user,
    target_user,
    previous_role_name,
    new_role_name,
):
    """Registra en auditoria el cambio de rol principal de un usuario."""

    description = build_user_role_change_description(
        acting_user=acting_user,
        target_user=target_user,
        previous_role_name=previous_role_name,
        new_role_name=new_role_name,
    )
    return create_audit_log(
        user=acting_user,
        action=AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED,
        resource_type=AUDIT_RESOURCE_TYPE_USER,
        resource_id=target_user.pk,
        description=description,
    )
