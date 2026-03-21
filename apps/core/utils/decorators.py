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


def role_required(role_name):
    """Exige que la vista solo se abra con el rol principal indicado."""
    normalized_role = (role_name or "").strip().lower()

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if get_primary_role(request.user) != normalized_role:
                return redirect("dashboard:home")
            return view_func(request, *args, **kwargs)

        return login_required(wrapper, login_url="/auth/login/")

    return decorator
