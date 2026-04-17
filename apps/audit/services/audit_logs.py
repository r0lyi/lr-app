"""Servicios para registrar eventos legibles en el historial de auditoria."""

from django.core.exceptions import ObjectDoesNotExist

from apps.audit.models import AuditLog

AUDIT_ACTION_USER_CREATED = "user_created"
AUDIT_ACTION_USER_PRIMARY_ROLE_CHANGED = "user_primary_role_changed"
AUDIT_ACTION_USER_ACCESS_STATE_CHANGED = "user_access_state_changed"
AUDIT_ACTION_USER_DEPARTMENT_CHANGED = "user_department_changed"
AUDIT_ACTION_USER_PROFILE_UPDATED = "user_profile_updated"
AUDIT_ACTION_USER_PASSWORD_CHANGED = "user_password_changed"
AUDIT_ACTION_USER_ACCOUNT_ACTIVATED = "user_account_activated"
AUDIT_ACTION_VACATION_REQUEST_REVIEWED = "vacation_request_reviewed"
AUDIT_RESOURCE_TYPE_USER = "user"
AUDIT_RESOURCE_TYPE_VACATION_REQUEST = "vacation_request"

ROLE_LABELS = {
    "employee": "Empleado",
    "rrhh": "RRHH",
    "admin": "Administrador",
}

VACATION_STATUS_LABELS = {
    "pending": "Pendiente",
    "approved": "Aprobada",
    "rejected": "Rechazada",
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


def get_vacation_status_label(status_name):
    """Traduce estados internos de vacaciones a etiquetas visibles."""

    normalized_status = (status_name or "").strip().lower()
    return VACATION_STATUS_LABELS.get(
        normalized_status,
        normalized_status.capitalize() if normalized_status else "Sin estado",
    )


def _get_user_email(user):
    """Devuelve un identificador estable para mensajes de auditoria."""

    return (getattr(user, "email", "") or "").strip() or f"Usuario #{user.pk}"


def _get_user_display(user):
    """Devuelve nombre y correo cuando existe ficha de empleado."""

    user_email = _get_user_email(user)
    try:
        employee_profile = user.employee_profile
    except (AttributeError, ObjectDoesNotExist):
        employee_profile = None

    if employee_profile is None:
        return user_email

    full_name = (
        f"{employee_profile.first_name or ''} {employee_profile.last_name or ''}"
    ).strip()
    if not full_name:
        return user_email
    return f"{full_name} ({user_email})"


def _get_employee_display(employee):
    """Formatea la persona propietaria de una solicitud de vacaciones."""

    full_name = f"{employee.first_name or ''} {employee.last_name or ''}".strip()
    try:
        user_email = _get_user_email(employee.user)
    except (AttributeError, ObjectDoesNotExist):
        user_email = ""

    if full_name and user_email:
        return f"{full_name} ({user_email})"
    return full_name or user_email or f"Empleado #{employee.pk}"


def _format_date(value):
    """Pinta fechas de negocio en formato cercano para RRHH."""

    if not value:
        return "Sin fecha"
    return value.strftime("%d/%m/%Y")


def _format_decimal(value):
    """Evita decimales innecesarios en dias solicitados."""

    if value is None:
        return "Sin dato"

    try:
        formatted = f"{value:.2f}"
    except (TypeError, ValueError):
        formatted = str(value)
    return formatted[:-3] if formatted.endswith(".00") else formatted


def _normalize_optional_text(value):
    """Normaliza texto opcional para comparar cambios reales."""

    normalized = (value or "").strip()
    return normalized or None


def _format_optional_value(value):
    """Convierte valores vacios en una etiqueta legible."""

    if value is None or value == "":
        return "Sin dato"
    return str(value)


def _format_field_change(label, previous_value, new_value):
    """Construye una pieza de texto para un cambio de atributo."""

    return (
        f"{label} de {_format_optional_value(previous_value)} "
        f"a {_format_optional_value(new_value)}"
    )


def _has_changed(previous_value, new_value):
    """Compara valores tratando texto vacio y None como equivalentes."""

    if isinstance(previous_value, str) or isinstance(new_value, str):
        return _normalize_optional_text(previous_value) != _normalize_optional_text(
            new_value
        )
    return previous_value != new_value


def build_user_created_description(*, acting_user, target_user):
    """Redacta la creacion de una cuenta pendiente de activacion."""

    actor_email = _get_user_email(acting_user)
    target_email = _get_user_email(target_user)
    target_dni = (target_user.dni or "").strip()
    return (
        f"{actor_email} creó la cuenta de {target_email} "
        f"con DNI {target_dni}. La cuenta quedó pendiente de activación."
    )


def log_user_created(*, acting_user, target_user):
    """Registra quien dio de alta a un usuario desde el panel admin."""

    return create_audit_log(
        user=acting_user,
        action=AUDIT_ACTION_USER_CREATED,
        resource_type=AUDIT_RESOURCE_TYPE_USER,
        resource_id=target_user.pk,
        description=build_user_created_description(
            acting_user=acting_user,
            target_user=target_user,
        ),
    )


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


def build_user_profile_updated_description(
    *,
    acting_user,
    target_user,
    field_changes,
):
    """Redacta una actualizacion de atributos visibles del usuario."""

    actor_label = _get_user_display(acting_user)
    target_label = _get_user_display(target_user)
    changes_text = "; ".join(
        _format_field_change(label, previous_value, new_value)
        for label, previous_value, new_value in field_changes
    )
    return (
        f"{actor_label} actualizó datos de {target_label}. "
        f"Cambios: {changes_text}."
    )


def log_user_profile_updated(*, acting_user, target_user, field_changes):
    """Registra cambios de datos personales o atributos editables."""

    clean_changes = [
        (label, previous_value, new_value)
        for label, previous_value, new_value in field_changes
        if _has_changed(previous_value, new_value)
    ]
    if not clean_changes:
        return None

    return create_audit_log(
        user=acting_user,
        action=AUDIT_ACTION_USER_PROFILE_UPDATED,
        resource_type=AUDIT_RESOURCE_TYPE_USER,
        resource_id=target_user.pk,
        description=build_user_profile_updated_description(
            acting_user=acting_user,
            target_user=target_user,
            field_changes=clean_changes,
        ),
    )


def build_user_password_changed_description(*, acting_user, target_user):
    """Redacta una actualizacion de contrasena sin exponer datos sensibles."""

    actor_label = _get_user_display(acting_user)
    target_label = _get_user_display(target_user)
    if acting_user.pk == target_user.pk:
        return f"{actor_label} cambió su contraseña desde el perfil."
    return f"{actor_label} cambió la contraseña de {target_label}."


def log_user_password_changed(*, acting_user, target_user):
    """Registra un cambio de contrasena como evento de seguridad."""

    return create_audit_log(
        user=acting_user,
        action=AUDIT_ACTION_USER_PASSWORD_CHANGED,
        resource_type=AUDIT_RESOURCE_TYPE_USER,
        resource_id=target_user.pk,
        description=build_user_password_changed_description(
            acting_user=acting_user,
            target_user=target_user,
        ),
    )


def build_user_account_activated_description(*, user):
    """Redacta la activacion de una cuenta desde enlace seguro."""

    user_label = _get_user_display(user)
    return f"{user_label} activó su cuenta y configuró su contraseña inicial."


def log_user_account_activated(*, user):
    """Registra cuando un usuario completa su acceso inicial."""

    return create_audit_log(
        user=user,
        action=AUDIT_ACTION_USER_ACCOUNT_ACTIVATED,
        resource_type=AUDIT_RESOURCE_TYPE_USER,
        resource_id=user.pk,
        description=build_user_account_activated_description(user=user),
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


def collect_vacation_request_review_changes(
    *,
    previous_status_name,
    new_status_name,
    previous_start_date,
    new_start_date,
    previous_end_date,
    new_end_date,
    previous_requested_days,
    new_requested_days,
    previous_hr_comment,
    new_hr_comment,
):
    """Devuelve cambios relevantes realizados al revisar una solicitud."""

    changes = []
    if (previous_status_name or "").strip().lower() != (
        new_status_name or ""
    ).strip().lower():
        changes.append(
            (
                "estado",
                get_vacation_status_label(previous_status_name),
                get_vacation_status_label(new_status_name),
            )
        )

    if previous_start_date != new_start_date:
        changes.append(
            (
                "fecha de inicio",
                _format_date(previous_start_date),
                _format_date(new_start_date),
            )
        )

    if previous_end_date != new_end_date:
        changes.append(
            (
                "fecha final",
                _format_date(previous_end_date),
                _format_date(new_end_date),
            )
        )

    if previous_requested_days != new_requested_days:
        changes.append(
            (
                "días solicitados",
                _format_decimal(previous_requested_days),
                _format_decimal(new_requested_days),
            )
        )

    normalized_previous_comment = _normalize_optional_text(previous_hr_comment)
    normalized_new_comment = _normalize_optional_text(new_hr_comment)
    if normalized_previous_comment != normalized_new_comment:
        if normalized_previous_comment and normalized_new_comment:
            comment_change = "comentario de RRHH actualizado"
        elif normalized_new_comment:
            comment_change = "comentario de RRHH añadido"
        else:
            comment_change = "comentario de RRHH eliminado"
        changes.append((comment_change, None, None))

    return changes


def build_vacation_request_review_description(
    *,
    acting_user,
    vacation_request,
    previous_status_name,
    new_status_name,
    previous_start_date,
    new_start_date,
    previous_end_date,
    new_end_date,
    previous_requested_days,
    new_requested_days,
    previous_hr_comment,
    new_hr_comment,
):
    """Redacta una revision de solicitud con los campos que cambiaron."""

    actor_label = _get_user_display(acting_user)
    employee_label = _get_employee_display(vacation_request.employee)
    changes = collect_vacation_request_review_changes(
        previous_status_name=previous_status_name,
        new_status_name=new_status_name,
        previous_start_date=previous_start_date,
        new_start_date=new_start_date,
        previous_end_date=previous_end_date,
        new_end_date=new_end_date,
        previous_requested_days=previous_requested_days,
        new_requested_days=new_requested_days,
        previous_hr_comment=previous_hr_comment,
        new_hr_comment=new_hr_comment,
    )
    formatted_changes = []
    for label, previous_value, new_value in changes:
        if previous_value is None and new_value is None:
            formatted_changes.append(label)
        else:
            formatted_changes.append(
                f"{label} de {previous_value} a {new_value}"
            )

    changes_text = "; ".join(formatted_changes) or "sin cambios relevantes"
    return (
        f"{actor_label} editó la solicitud de vacaciones de {employee_label}. "
        f"Cambios: {changes_text}."
    )


def log_vacation_request_reviewed(
    *,
    acting_user,
    vacation_request,
    previous_status_name,
    new_status_name,
    previous_start_date,
    new_start_date,
    previous_end_date,
    new_end_date,
    previous_requested_days,
    new_requested_days,
    previous_hr_comment,
    new_hr_comment,
):
    """Registra una revision de RRHH/admin si realmente hubo cambios."""

    changes = collect_vacation_request_review_changes(
        previous_status_name=previous_status_name,
        new_status_name=new_status_name,
        previous_start_date=previous_start_date,
        new_start_date=new_start_date,
        previous_end_date=previous_end_date,
        new_end_date=new_end_date,
        previous_requested_days=previous_requested_days,
        new_requested_days=new_requested_days,
        previous_hr_comment=previous_hr_comment,
        new_hr_comment=new_hr_comment,
    )
    if not changes:
        return None

    return create_audit_log(
        user=acting_user,
        action=AUDIT_ACTION_VACATION_REQUEST_REVIEWED,
        resource_type=AUDIT_RESOURCE_TYPE_VACATION_REQUEST,
        resource_id=vacation_request.pk,
        description=build_vacation_request_review_description(
            acting_user=acting_user,
            vacation_request=vacation_request,
            previous_status_name=previous_status_name,
            new_status_name=new_status_name,
            previous_start_date=previous_start_date,
            new_start_date=new_start_date,
            previous_end_date=previous_end_date,
            new_end_date=new_end_date,
            previous_requested_days=previous_requested_days,
            new_requested_days=new_requested_days,
            previous_hr_comment=previous_hr_comment,
            new_hr_comment=new_hr_comment,
        ),
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
