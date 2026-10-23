# usuarios/infrastructure/api/v1/views/responder.py — la respuesta de un inicio de sesión de la SPA (módulo 92)
from rest_framework.response import Response

from usuarios.application.shared.dtos.segundo_factor_pendiente_output_dto import SegundoFactorPendienteOutputDTO
from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO
from usuarios.infrastructure.api.sessions.peticion import poner_cookie_dispositivo
from usuarios.infrastructure.api.v1.views.cookie_mfa import borrar_cookie_mfa, poner_cookie_mfa
from usuarios.infrastructure.api.v1.views.cookie_refresh import poner_cookie_refresh


def responder(resultado: SesionAbiertaOutputDTO | SegundoFactorPendienteOutputDTO) -> Response:
    """Lo que devuelve un inicio de sesión de la SPA (contraseña, segundo factor, passkey): la sesión o el segundo paso."""
    if isinstance(resultado, SegundoFactorPendienteOutputDTO):
        respuesta = Response({"segundo_factor": resultado.factores})
        poner_cookie_mfa(respuesta, resultado.clave)
        return respuesta
    respuesta = Response({"access": resultado.tokens.access})
    poner_cookie_refresh(respuesta, resultado.tokens.refresh)
    poner_cookie_dispositivo(respuesta, resultado)
    borrar_cookie_mfa(respuesta)
    return respuesta
