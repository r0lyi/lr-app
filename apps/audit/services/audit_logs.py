"""Servicios para registrar eventos legibles en el historial de auditoria."""

from apps.audit.models import AuditLog

AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED = "user_primary_role_changed"
AUDIT_ACTION_USER_ACCESS_STATE_CHANGED = "user_access_state_changed"
AUDIT_ACTION_USER_DEPARTMENT_CHANGED = "user_department_changed"
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


def build_user_access_state_change_description(
    *,
    acting_user,
    target_user,
    is_active,
):
    """Redacta un mensaje claro sobre activacion o desactivacion de acceso."""

    actor_email = (acting_user.email or "").strip()
    target_email = (target_user.email or "").strip()
    action_text = "activó" if is_active else "desactivó"
    return f"{actor_email} {action_text} el acceso al sistema de {target_email}."


def log_user_access_state_changed(*, acting_user, target_user, is_active):
    """Registra en auditoria la activacion o desactivacion de una cuenta."""

    description = build_user_access_state_change_description(
        acting_user=acting_user,
        target_user=target_user,
        is_active=is_active,
    )
    return create_audit_log(
        user=acting_user,
        action=AUDIT_ACTION_USER_ACCESS_STATE_CHANGED,
        resource_type=AUDIT_RESOURCE_TYPE_USER,
        resource_id=target_user.pk,
        description=description,
    )


def build_user_department_change_description(
    *,
    acting_user,
    target_user,
    previous_department_name,
    new_department_name,
):
    """Redacta un mensaje claro cuando cambia el departamento de un empleado."""

    actor_email = (acting_user.email or "").strip()
    target_email = (target_user.email or "").strip()
    previous_department_label = previous_department_name or "Sin departamento"
    new_department_label = new_department_name or "Sin departamento"
    return (
        f"{actor_email} cambió el departamento de {target_email} "
        f"de {previous_department_label} a {new_department_label}."
    )


def log_user_department_changed(
    *,
    acting_user,
    target_user,
    previous_department_name,
    new_department_name,
):
    """Registra en auditoria el cambio de departamento del empleado."""

    description = build_user_department_change_description(
        acting_user=acting_user,
        target_user=target_user,
        previous_department_name=previous_department_name,
        new_department_name=new_department_name,
    )
    return create_audit_log(
        user=acting_user,
        action=AUDIT_ACTION_USER_DEPARTMENT_CHANGED,
        resource_type=AUDIT_RESOURCE_TYPE_USER,
        resource_id=target_user.pk,
        description=description,
    )
