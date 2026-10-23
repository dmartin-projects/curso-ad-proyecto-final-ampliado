# usuarios/infrastructure/api/v1/views/cookie_mfa.py — la cookie del login a medias (módulo 92)
from django.conf import settings

COOKIE_MFA = "mfa"  # el login a medias (falta el segundo factor). Solo viaja a /api/v1/auth/


def poner_cookie_mfa(response, clave: str):
    """La clave del login pendiente: HttpOnly (JavaScript no la lee), Strict y con el path de la autenticación, como
    la del refresh. Nunca en el cuerpo ni en una URL: en la vuelta de un proveedor, la URL acaba en el historial."""
    cfg = settings.JWT_REFRESH_COOKIE
    response.set_cookie(
        COOKIE_MFA, clave, max_age=settings.MFA_PENDIENTE_SEGUNDOS, path=cfg["path"], httponly=True,
        secure=cfg["secure"], samesite="Strict",
    )  # fmt: skip


def borrar_cookie_mfa(response):
    response.delete_cookie(COOKIE_MFA, path=settings.JWT_REFRESH_COOKIE["path"], samesite="Strict")
