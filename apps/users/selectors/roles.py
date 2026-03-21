PRIMARY_ROLE_PRIORITY = ("admin", "rrhh", "employee")


def get_user_role_names(user):
    return {
        name.strip().lower()
        for name in user.roles.values_list("name", flat=True)
        if name
    }


def has_role(user, role_name):
    normalized_role = (role_name or "").strip().lower()
    if not normalized_role:
        return False
    return normalized_role in get_user_role_names(user)


def get_primary_role(user):
    role_names = get_user_role_names(user)

    if getattr(user, "is_superuser", False):
        return "admin"

    for role_name in PRIMARY_ROLE_PRIORITY:
        if role_name in role_names:
            return role_name
    return None
