"""Vistas HTTP del flujo publico de login, activacion y logout."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from apps.core.utils.client_ip import _client_ip
from apps.core.utils.decorators import anonymous_required
from apps.core.utils.responses_toast import toast_response as _toast_response 
from apps.core.utils.responses_toast import rate_limit_response as _rate_limit_response

from apps.core.utils.rate_limits import (
    is_rate_limited,
    register_rate_limit_attempt,
    reset_rate_limit,
)
from apps.users.forms import RequestActivationForm, SetPasswordForm, LoginForm
from apps.users.services.auth_service import request_activation, validate_token, set_password


@anonymous_required
def request_activation_view(request):
    """Gestiona la solicitud del email de activacion o recuperacion."""

    form = RequestActivationForm(request.POST or None)

    if request.method == "POST":
        identifier = request.POST.get("dni", "")
        if is_rate_limited(
            "activation",
            client_ip=_client_ip(request),
            identifier=identifier,
            limit=settings.ACTIVATION_RATE_LIMIT_ATTEMPTS,
        ):
            return _rate_limit_response(
                request,
                "Demasiados intentos. Intentalo de nuevo mas tarde.",
            )

        if form.is_valid():
            register_rate_limit_attempt(
                "activation",
                client_ip=_client_ip(request),
                identifier=form.cleaned_data["dni"],
                window_seconds=settings.ACTIVATION_RATE_LIMIT_WINDOW,
            )
            _, notification_message = request_activation(form.cleaned_data["dni"])

            # HTMX — retorna solo el fragmento HTML
            if request.headers.get("HX-Request"):
                return _toast_response(
                    request=request,
                    variant="info",
                    title="Notificacion enviada",
                    message=notification_message,
                    duration=5000,
                )

            messages.info(request, notification_message)
            form = RequestActivationForm()
        else:
            validation_message = "Debes introducir tu DNI."
            if request.headers.get("HX-Request"):
                return _toast_response(
                    request=request,
                    variant="error",
                    title="Error de validacion",
                    message=validation_message,
                    duration=4500,
                )
            messages.error(request, validation_message)

    return render(request, "users/pages/request_activation.html", {"form": form})


@anonymous_required
def set_password_view(request, token):
    """Valida el token y permite fijar la contraseña inicial o recuperada."""

    user = validate_token(token)

    if not user:
        return render(request, "users/pages/invalid_token.html")

    form = SetPasswordForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            set_password(user, form.cleaned_data["password1"])
            messages.success(request, "Tu contraseña se actualizo correctamente.")
            return redirect("auth:login")

        form_error = form.non_field_errors()
        if form_error:
            messages.error(request, form_error[0])
        else:
            messages.error(request, "Completa los campos obligatorios del formulario.")

    return render(
        request,
        "users/pages/set_password.html",
        {"form": form, "token": token},
    )


@anonymous_required
def login_view(request):
    """Autentica al usuario por DNI y lo envia al dispatcher del dashboard."""

    form = LoginForm(request.POST or None)

    if request.method == "POST":
        identifier = request.POST.get("dni", "")
        if is_rate_limited(
            "login",
            client_ip=_client_ip(request),
            identifier=identifier,
            limit=settings.LOGIN_RATE_LIMIT_ATTEMPTS,
        ):
            return _rate_limit_response(
                request,
                "Demasiados intentos. Intentalo de nuevo mas tarde.",
            )

        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["dni"],
                password=form.cleaned_data["password"],
            )

            if user:
                reset_rate_limit(
                    "login",
                    client_ip=_client_ip(request),
                    identifier=form.cleaned_data["dni"],
                )
                login(request, user)
                if request.headers.get("HX-Request"):
                    # HTMX necesita una redireccion explicita para navegar fuera del fragmento.
                    response = HttpResponse()
                    response["HX-Redirect"] = "/dashboard/"
                    return response
                return redirect("dashboard:home")

            register_rate_limit_attempt(
                "login",
                client_ip=_client_ip(request),
                identifier=form.cleaned_data["dni"],
                window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW,
            )
            form.add_error(None, "DNI o contraseña incorrectos.")
        else:
            form.add_error(None, "Debes completar DNI y contraseña.")

        error_message = form.non_field_errors()[0]
        if request.headers.get("HX-Request"):
            return _toast_response(
                request=request,
                variant="error",
                title="Error de acceso",
                message=error_message,
                duration=4500,
            )
        messages.error(request, error_message)

    return render(request, "users/pages/login.html", {"form": form})


def logout_view(request):
    """Cierra la sesion actual y devuelve al login."""

    if request.method == "POST":
        logout(request)
    return redirect("auth:login")
