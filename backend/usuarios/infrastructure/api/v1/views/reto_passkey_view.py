# usuarios/infrastructure/api/v1/views/reto_passkey_view.py — entrar con una passkey, sin contraseña: el reto (módulo 92)
import secrets

from django.conf import settings
from rest_framework.response import Response

from usuarios.application.pedir_reto_use_case.dtos.pedir_reto_input_dto import PedirRetoInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.cookie_reto import COOKIE_RETO, RUTA_RETO
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class RetoPasskeyView(VistaPublicaAuth):
    throttle_scope = "passkey"

    def post(self, request, **kwargs):
        clave = secrets.token_urlsafe(32)
        respuesta = Response(container.pedir_reto().ejecutar(PedirRetoInputDTO(f"entrar:{clave}")))
        respuesta.set_cookie(
            COOKIE_RETO, clave, max_age=300, path=RUTA_RETO, httponly=True,
            secure=settings.JWT_REFRESH_COOKIE["secure"], samesite="Strict",
        )  # fmt: skip
        return respuesta
