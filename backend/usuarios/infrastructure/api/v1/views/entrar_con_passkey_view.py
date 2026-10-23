# usuarios/infrastructure/api/v1/views/entrar_con_passkey_view.py — entrar con una passkey, sin contraseña (módulo 92)
from usuarios.application.entrar_con_passkey_use_case.dtos.entrar_con_passkey_input_dto import (
    EntrarConPasskeyInputDTO,
)
from usuarios.domain.enums.canal import Canal
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import contexto_de
from usuarios.infrastructure.api.v1.views.cookie_reto import COOKIE_RETO, RUTA_RETO
from usuarios.infrastructure.api.v1.views.responder import responder
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class EntrarConPasskeyView(VistaPublicaAuth):
    throttle_scope = "passkey"

    def post(self, request, **kwargs):
        entrada = EntrarConPasskeyInputDTO(
            request.COOKIES.get(COOKIE_RETO), request.data.get("respuesta") or {}, Canal.SPA, contexto_de(request)
        )
        respuesta = responder(container.entrar_con_passkey().ejecutar(entrada))
        respuesta.delete_cookie(COOKIE_RETO, path=RUTA_RETO, samesite="Strict")
        return respuesta
