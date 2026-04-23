"""Utilidades de rate limiting sobre la cache de Django."""

from hashlib import sha256

from django.core.cache import cache


def _normalize_identifier(identifier=None):
    """Normaliza IPs y DNIs antes de construir claves de cache."""

    value = str(identifier or "anonymous").strip().lower()
    return value or "anonymous"


def build_rate_limit_key(prefix=None, *, client_ip, identifier):
    """Genera una clave de cache anonima para el contador de intentos."""

    raw_key = (
        f"{prefix}:{_normalize_identifier(client_ip)}:"
        f"{_normalize_identifier(identifier)}"
    )
    digest = sha256(raw_key.encode("utf-8")).hexdigest()
    return f"rate-limit:{prefix}:{digest}"


def is_rate_limited(prefix=None, *, client_ip, identifier, limit):
    """Indica si ya se alcanzo el limite de intentos configurado."""

    key = build_rate_limit_key(prefix, client_ip=client_ip, identifier=identifier)
    attempts = int(cache.get(key, 0) or 0)
    return attempts >= limit


def register_rate_limit_attempt(prefix=None, *, client_ip, identifier, window_seconds):
    """Incrementa el contador de intentos y renueva su ventana de expiracion."""

    key = build_rate_limit_key(prefix, client_ip=client_ip, identifier=identifier)
    attempts = int(cache.get(key, 0) or 0) + 1
    cache.set(key, attempts, timeout=window_seconds)
    return attempts


def reset_rate_limit(prefix=None, *, client_ip, identifier):
    """Borra el contador asociado a un login o activacion exitosa."""

    key = build_rate_limit_key(prefix, client_ip=client_ip, identifier=identifier)
    cache.delete(key)
