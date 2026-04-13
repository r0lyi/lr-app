"""Decoradores compartidos para proteger vistas publicas y privadas."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from apps.users.selectors import get_primary_role


def anonymous_required(view_func):
    """Impide acceder a vistas anonimas cuando ya existe sesion iniciada."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return view_func(request, *args, **kwargs)

    return wrapper


def role_required(role_name, *, allow_admin=False, allow_rrhh=False):
    """Exige un rol principal concreto y opcionalmente permite otros accesos."""
    normalized_role = (role_name or "").strip().lower()

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            current_role = get_primary_role(request.user)

            if current_role == normalized_role:
                return view_func(request, *args, **kwargs)

            if allow_admin and current_role == "admin":
                return view_func(request, *args, **kwargs)

            if allow_rrhh and current_role == "rrhh":
                return view_func(request, *args, **kwargs)

            if current_role != normalized_role:
                return redirect("dashboard:home")

        return login_required(wrapper, login_url="/auth/login/")

    return decorator
