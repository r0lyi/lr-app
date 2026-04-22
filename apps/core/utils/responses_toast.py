"""Respuestas HTTP reutilizables para toasts y rate limiting."""

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def toast_response(request, variant, title, message, duration=5000):
    """Renderiza el HTML de un toast para respuestas clasicas o HTMX."""

    return HttpResponse(
        render_to_string(
            "components/feedback/toast_card.html",
            {
                "variant": variant,
                "title": title,
                "message": message,
                "duration": duration,
            },
            request=request,
        )
    )


def rate_limit_response(request, message):
    """Devuelve un toast HTMX o un `429` plano segun el tipo de request."""

    if request.headers.get("HX-Request"):
        return toast_response(
            request,
            variant="error",
            title=_("Demasiados intentos"),
            message=message,
            duration=4500,
        )
    return HttpResponse(message, status=429)
