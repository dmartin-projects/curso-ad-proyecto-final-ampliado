# usuarios/infrastructure/api/v1/views/cookie_social.py — la cookie de la transacción del social login (módulo 91)
from django.conf import settings

from usuarios.application.empezar_login_social_use_case.dtos.ida_al_proveedor_output_dto import (
    IdaAlProveedorOutputDTO,
)
from usuarios.domain.enums.proveedor import Proveedor


def cookie_social(proveedor: str) -> dict:
    return {"key": f"social_{proveedor}", "path": f"/api/v1/auth/social/{proveedor}/"}


def recordar(respuesta, proveedor: Proveedor, ida: IdaAlProveedorOutputDTO) -> None:
    """La clave de la transacción, en una cookie que solo viaja a la vuelta de ESE proveedor (path), que JavaScript no
    lee (HttpOnly) y que dura lo que el inicio de sesión. SameSite=Lax la manda en la vuelta normal: una navegación
    GET desde el proveedor. La de Apple es un POST desde appleid.apple.com, que con Lax llegaría SIN la cookie:
    SameSite=None (que exige Secure). No es una credencial: sin el `state` de su transacción no sirve de nada."""
    respuesta.set_cookie(
        **cookie_social(proveedor),
        value=ida.clave,
        max_age=settings.SOCIAL_LOGIN_SEGUNDOS,
        httponly=True,
        secure=True if ida.form_post else settings.JWT_REFRESH_COOKIE["secure"],
        samesite="None" if ida.form_post else "Lax",
    )
