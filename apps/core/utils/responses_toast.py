from django.http import HttpResponse
from django.template.loader import render_to_string


def toast_response(request, variant, title, message, duration=5000):
    return HttpResponse(
        render_to_string(
            "components/toast_card.html",
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
    if request.headers.get("HX-Request"):
        return toast_response(
            request,
            variant="error",
            title="Demasiados intentos",
            message=message,
            duration=4500,
        )
    return HttpResponse(message, status=429)