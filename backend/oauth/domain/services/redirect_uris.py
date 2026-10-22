# oauth/domain/services/redirect_uris.py — qué redirect URIs se pueden registrar (módulo 90)
from ipaddress import ip_address
from urllib.parse import urlsplit

from oauth.domain.exceptions.redirect_uri_no_valida_exception import RedirectUriNoValidaException


def es_loopback(host: str | None) -> bool:
    """127.0.0.1 o [::1]. "localhost" NO (RFC 8252 §8.3): puede resolverse a otra máquina o estar mal configurado."""
    try:
        return host is not None and ip_address(host).is_loopback
    except ValueError:
        return False


def validar_redirect_uri(uri: str) -> str:
    """Una redirect URI que se registra para compararla EXACTA (sin comodines) en cada petición."""
    partes = urlsplit(uri)
    if not partes.scheme or partes.fragment or "#" in uri or "*" in uri:
        raise RedirectUriNoValidaException(f"«{uri}»: absoluta, sin fragmento (#) y sin comodines.")
    if partes.scheme == "https" and partes.hostname:
        return uri
    if partes.scheme == "http" and es_loopback(partes.hostname):
        return uri  # RFC 8252 §7.3: el puerto puede cambiar en cada petición (el servidor lo permite)
    raise RedirectUriNoValidaException(f"«{uri}»: https, o http solo a 127.0.0.1 o [::1] (loopback).")
