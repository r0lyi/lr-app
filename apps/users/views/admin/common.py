"""Helpers compartidos entre las vistas admin del dominio users."""

from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme


def redirect_to_admin_users_target(request):
    """Devuelve una redireccion segura al destino deseado tras guardar."""

    next_url = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("dashboard:admin-users")


def parse_boolean_post_value(value):
    """Normaliza valores booleanos que llegan desde formularios HTML."""

    normalized_value = (value or "").strip().lower()
    if normalized_value in {"1", "true", "on", "yes"}:
        return True
    if normalized_value in {"0", "false", "off", "no"}:
        return False
    return None
