# usuarios/infrastructure/api/sessions/peticion.py — la sesión y el navegador de una petición (módulo 92)
#
#   sid_de                    el sid del access token de la petición
#   contexto_de               desde dónde entra alguien (user agent, IP, la cookie `dispositivo`)
#   poner_cookie_dispositivo  la cookie que reconoce a este navegador la próxima vez
from rest_framework.throttling import BaseThrottle
from rest_framework_simplejwt.tokens import Token

from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO
from usuarios.domain.vo.contexto import Contexto

COOKIE_DISPOSITIVO = "dispositivo"


def sid_de(request) -> str | None:
    """El sid del access token de la petición (None con un token OAuth, sin token o con uno sin sesión)."""
    return request.auth.get("sid") if isinstance(request.auth, Token) else None


def contexto_de(request) -> Contexto:
    return Contexto(
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        ip=BaseThrottle().get_ident(request),  # la del navegador, detrás de Vercel y Caddy (NUM_PROXIES, módulo 86)
        dispositivo=request.COOKIES.get(COOKIE_DISPOSITIVO, "")[:100],
    )


def poner_cookie_dispositivo(respuesta, sesion: SesionAbiertaOutputDTO) -> None:
    """Una cookie por navegador, para reconocerlo la próxima vez (y avisar si es nuevo). No es una credencial: no
    abre nada. SameSite=None porque la vuelta de Apple es un POST de otro sitio (módulo 91 §5): con Lax llegaría sin
    ella y cada entrada con Apple parecería de un dispositivo nuevo."""
    respuesta.set_cookie(
        COOKIE_DISPOSITIVO, sesion.dispositivo, max_age=400 * 24 * 3600, path="/api/", httponly=True, secure=True,
        samesite="None",
    )  # fmt: skip
