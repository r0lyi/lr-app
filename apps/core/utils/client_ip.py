"""Helpers pequeños para extraer datos del request HTTP."""


def _client_ip(request):
    """Obtiene la IP remota que Django ha asociado al request."""

    return request.META.get("REMOTE_ADDR", "")
