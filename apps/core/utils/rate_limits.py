from hashlib import sha256

from django.core.cache import cache

# Servicios relacionados con límites de intentos para login y 
# activación de cuenta, usando cache para almacenar los intentos y bloqueos

# Normaliza el identificador (IP o DNI) para construir la clave de cache, evitando espacios y mayúsculas
def _normalize_identifier(identifier = None):
    value = str(identifier or "anonymous").strip().lower()
    return value or "anonymous"

# Construye la clave de cache para un intento de acción, usando un hash para anonimizar los datos
def build_rate_limit_key(prefix = None, *, client_ip, identifier):
    raw_key = f'''{prefix}:{_normalize_identifier(client_ip)}:{_normalize_identifier(identifier)}'''
    digest = sha256(raw_key.encode('utf-8')).hexdigest()
    return f'''rate-limit:{prefix}:{digest}'''

# Verifica si el cliente ha excedido el límite de intentos para la acción, usando la clave de cache
def is_rate_limited(prefix = None, *, client_ip, identifier, limit):
    key = build_rate_limit_key(prefix, client_ip = client_ip, identifier = identifier)
    attempts = int(cache.get(key, 0) or 0)
    return attempts >= limit

# Registra un intento para la acción, incrementando el contador en cache y estableciendo el tiempo de bloqueo
def register_rate_limit_attempt(prefix = None, *, client_ip, identifier, window_seconds):
    key = build_rate_limit_key(prefix, client_ip = client_ip, identifier = identifier)
    attempts = int(cache.get(key, 0) or 0) + 1
    cache.set(key, attempts, timeout = window_seconds)
    return attempts

# Resetea el contador de intentos para la acción, eliminando la clave de cache
def reset_rate_limit(prefix = None, *, client_ip, identifier):
    key = build_rate_limit_key(prefix, client_ip = client_ip, identifier = identifier)
    cache.delete(key)
