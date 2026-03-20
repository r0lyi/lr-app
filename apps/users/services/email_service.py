import logging
from email.message import MIMEPart
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

SUPPORTED_EMAIL_PROVIDERS = {"console", "resend"}

INLINE_LOGO_CID = "company-logo"

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

def _build_logo_attachment():
    logo_path = Path(settings.BASE_DIR) / "static" / "images" / "logo500x200.png"
    if not logo_path.exists():
        return None

    return {
        "filename": logo_path.name,
        "content": logo_path.read_bytes(),
        "content_type": "image/png",
        "content_id": INLINE_LOGO_CID,
    }


# Construye el asunto, cuerpo HTML y texto plano para el email de activación
def build_activation_email_message(token):
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    activation_url = f"{frontend_url}/auth/set-password/{token}/"
    logo_url = f"cid:{INLINE_LOGO_CID}"
    context = {
        "app_name": "Sistema de Gestion de Vacaciones",
        "company_name": "LR Clean & Service",
        "activation_url": activation_url,
        "logo_url": logo_url,
        "expires_in_hours": 24,
    }
    return {
        "subject": "Cree su contraseña para entrar en el sistema",
        "html": render_to_string("emails/activation_email.html", context),
        "text": render_to_string("emails/activation_email.txt", context),
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
    if attachment.get("content_id"):
        normalized["content_id"] = attachment["content_id"]
    elif attachment.get("inline_content_id"):
        normalized["content_id"] = attachment["inline_content_id"]
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
        content_id = attachment.get("content_id") or attachment.get("inline_content_id")
        if content_id:
            content_type = attachment.get("content_type") or "image/png"
            maintype, subtype = content_type.split("/", 1)
            inline_part = MIMEPart()
            inline_part.set_content(
                attachment["content"],
                maintype=maintype,
                subtype=subtype,
                disposition="inline",
                cid=f"<{content_id}>",
                filename=attachment["filename"],
            )
            message.attach(inline_part)
        else:
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
    attachments = []
    logo_attachment = _build_logo_attachment()
    if logo_attachment:
        attachments.append(logo_attachment)
    send_email_message(
        to=[email],
        subject=payload["subject"],
        html=payload["html"],
        text=payload["text"],
        attachments=attachments,
    )
