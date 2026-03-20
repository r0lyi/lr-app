import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

SUPPORTED_EMAIL_PROVIDERS = {"console", "resend"}

# Servicios relacionados con envío de emails, construcción de mensajes y selección de proveedor
def get_email_provider():
    provider = getattr(settings, "EMAIL_PROVIDER", "").strip().lower()
    if not provider:
        provider = "resend" if getattr(settings, "RESEND_API_KEY", "").strip() else "console"
    if provider not in SUPPORTED_EMAIL_PROVIDERS:
        raise ValueError(
            f"Unsupported EMAIL_PROVIDER '{provider}'. "
            f"Supported values: {', '.join(sorted(SUPPORTED_EMAIL_PROVIDERS))}."
        )
    return provider

# Construye el asunto, cuerpo HTML y texto plano para el email de activación
def build_activation_email_message(token):
    activation_url = f"{settings.FRONTEND_URL}/auth/set-password/{token}/"
    return {
        "subject": _("Create your access password"),
        "html": (
            f"<h2>{_('Welcome to the system')}</h2>"
            f"<p>{_('Click the following link to create your password:')}</p>"
            f'<a href="{activation_url}">{_("Create password")}</a>'
            f"<p>{_('This link expires in 24 hours.')}</p>"
        ),
        "text": (
            f"{_('Welcome to the system.')}\n"
            f"{_('Click the following link to create your password:')}\n"
            f"{activation_url}\n"
            f"{_('This link expires in 24 hours.')}\n"
        ),
    }

# Normaliza el formato de adjuntos para Resend, asegurando que el contenido sea una lista de bytes
def _normalize_resend_attachment(attachment):
    content = attachment["content"]
    if isinstance(content, bytes):
        content = list(content)

    normalized = {
        "filename": attachment["filename"],
        "content": content,
    }
    if attachment.get("content_type"):
        normalized["content_type"] = attachment["content_type"]
    return normalized

# Envía el email usando el proveedor configurado, maneja adjuntos y loguea el resultado
def _send_via_django_backend(*, to, subject, html, text="", attachments=None):
    attachments = attachments or []
    connection = get_connection(
        backend=getattr(
            settings,
            "EMAIL_BACKEND",
            "django.core.mail.backends.console.EmailBackend",
        )
    )
    message = EmailMultiAlternatives(
        subject=str(subject),
        body=text or "",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=list(to),
        connection=connection,
    )
    if html:
        message.attach_alternative(html, "text/html")
    for attachment in attachments:
        message.attach(
            attachment["filename"],
            attachment["content"],
            attachment.get("content_type"),
        )
    return message.send()

# Envía el email usando la API de Resend, maneja adjuntos y loguea el resultado
def _send_via_resend(*, to, subject, html, text="", attachments=None):
    try:
        import resend
    except ImportError as exc:
        raise RuntimeError(
            "El proveedor Resend esta configurado, pero el paquete 'resend' no esta instalado."
        ) from exc

    api_key = getattr(settings, "RESEND_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Falta RESEND_API_KEY para enviar correos con Resend.")

    resend.api_key = api_key
    payload = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": list(to),
        "subject": str(subject),
    }
    if html:
        payload["html"] = html
    if text:
        payload["text"] = text
    if attachments:
        payload["attachments"] = [
            _normalize_resend_attachment(attachment)
            for attachment in attachments
        ]

    response = resend.Emails.send(payload)
    return 1 if response and response.get("id") else 0


# Función principal para enviar emails, selecciona el proveedor configurado y loguea el resultado
def send_email_message(*, to, subject, html, text="", attachments=None):
    attachments = attachments or []
    provider = get_email_provider()
    if provider == "resend":
        sent = _send_via_resend(
            to=to,
            subject=subject,
            html=html,
            text=text,
            attachments=attachments,
        )
    else:
        sent = _send_via_django_backend(
            to=to,
            subject=subject,
            html=html,
            text=text,
            attachments=attachments,
        )
    logger.info("Email dispatched", extra={"to": list(to), "subject": str(subject), "sent": sent})
    return sent


# Función específica para enviar el email de activación, construye el mensaje y lo envía
def send_activation_email(email: str, token: str) -> None:
    payload = build_activation_email_message(token)
    send_email_message(
        to=[email],
        subject=payload["subject"],
        html=payload["html"],
        text=payload["text"],
    )
