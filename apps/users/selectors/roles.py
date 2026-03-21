"""Utilidades para consultar y resolver el rol principal de un usuario."""

PRIMARY_ROLE_PRIORITY = ("admin", "rrhh", "employee")


def get_user_role_names(user):
    """Devuelve los nombres de rol normalizados del usuario."""
    return {
        name.strip().lower()
        for name in user.roles.values_list("name", flat=True)
        if name
    }


def has_role(user, role_name):
    """Indica si un usuario tiene asignado un rol concreto."""
    normalized_role = (role_name or "").strip().lower()
    if not normalized_role:
        return False
    return normalized_role in get_user_role_names(user)


def get_primary_role(user):
    """Resuelve el rol principal segun la prioridad admin > rrhh > employee."""
    role_names = get_user_role_names(user)

    # Los superusuarios de Django se tratan como admin aunque no se haya
    # sincronizado explicitamente su rol en la tabla intermedia.
    if getattr(user, "is_superuser", False):
        return "admin"

    for role_name in PRIMARY_ROLE_PRIORITY:
        if role_name in role_names:
            return role_name
    return None
