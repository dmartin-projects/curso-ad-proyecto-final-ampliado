# usuarios/infrastructure/api/v1/views/vuelta_social_view.py — la vuelta del proveedor (módulos 91 y 92)
#
# Una NAVEGACIÓN del navegador: traduce los errores del dominio a una redirección a la SPA (?error_social=<codigo>) en
# vez de dejárselos al exception handler, que responde JSON.
from django.utils.cache import add_never_cache_headers
from rest_framework.parsers import FormParser

from core.domain.exceptions.dominio_exception import DominioException
from usuarios.application.completar_login_social_use_case.dtos.completar_login_social_input_dto import (
    CompletarLoginSocialInputDTO,
)
from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.application.shared.dtos.segundo_factor_pendiente_output_dto import SegundoFactorPendienteOutputDTO
from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.factor import Factor
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import contexto_de, poner_cookie_dispositivo
from usuarios.infrastructure.api.sessions.sesion_de_django import (
    PENDIENTE_DJANGO,
    SEGUNDO_FACTOR_AUTORIZACION,
    entrar_en_django,
)
from usuarios.infrastructure.api.v1.views.a_la_spa import a_la_spa
from usuarios.infrastructure.api.v1.views.cookie_mfa import poner_cookie_mfa
from usuarios.infrastructure.api.v1.views.cookie_refresh import poner_cookie_refresh
from usuarios.infrastructure.api.v1.views.cookie_social import cookie_social
from usuarios.infrastructure.api.v1.views.rutas_autorizacion import LOGIN_AUTORIZACION
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class VueltaSocialView(VistaPublicaAuth):
    """La redirect URI registrada en el proveedor. GET (code y state en la query) o, en Apple, POST (form_post)."""

    parser_classes = [FormParser]  # el form_post de Apple es application/x-www-form-urlencoded

    def get(self, request, proveedor, **kwargs):
        return self._vuelta(request, proveedor, request.query_params)

    def post(self, request, proveedor, **kwargs):
        return self._vuelta(request, proveedor, request.data)

    def _vuelta(self, request, proveedor, datos):
        cookie = cookie_social(proveedor)
        try:
            entrada = CompletarLoginSocialInputDTO(
                Proveedor.de(proveedor), request.COOKIES.get(cookie["key"]), {k: datos.get(k) for k in datos}
            )
            hecho = container.completar_login_social().ejecutar(entrada)
            if hecho.proposito is Proposito.VINCULAR:
                respuesta = a_la_spa("/acceso", vinculada=proveedor)
            elif hecho.proposito is Proposito.REAUTENTICAR:  # módulo 92, ej. 3: de vuelta a la página, ya confirmado
                respuesta = a_la_spa(hecho.volver, reautenticada=proveedor)
            elif hecho.proposito is Proposito.AUTORIZAR:
                # Ejercicio 3: la sesión del authorization server (la de Django, cookie solo para /api/oauth/), por
                # el mismo IniciarSesionUseCase; y de vuelta a /authorize, que enseñará el consentimiento
                inicio = IniciarSesionInputDTO(
                    hecho.usuario_id, Factor.PROVEEDOR, Canal.AUTORIZACION, contexto_de(request), hecho.volver
                )
                resultado = container.iniciar_sesion().ejecutar(inicio)
                if isinstance(resultado, SegundoFactorPendienteOutputDTO):  # módulo 92: antes, el segundo factor
                    request.session[PENDIENTE_DJANGO] = resultado.clave
                    return self._sin_cache(a_la_spa(SEGUNDO_FACTOR_AUTORIZACION, next=hecho.volver), cookie)
                entrar_en_django(request, resultado, hecho.usuario_id)
                respuesta = a_la_spa(hecho.volver)
            else:
                # Los MISMOS tokens que con la contraseña: el refresh, en su cookie; el access lo pide la SPA al
                # arrancar (POST /auth/refresh/, como tras un F5). Los del proveedor ni se guardan ni llegan aquí
                inicio = IniciarSesionInputDTO(
                    hecho.usuario_id, Factor.PROVEEDOR, Canal.SPA, contexto_de(request), hecho.volver
                )
                resultado = container.iniciar_sesion().ejecutar(inicio)
                if isinstance(resultado, SegundoFactorPendienteOutputDTO):
                    # Módulo 92: la cuenta tiene MFA. La SPA pide el segundo factor; la clave, en su cookie
                    respuesta = a_la_spa("/login/segundo-factor", volver=hecho.volver)
                    poner_cookie_mfa(respuesta, resultado.clave)
                else:
                    respuesta = a_la_spa(hecho.volver)
                    poner_cookie_refresh(respuesta, resultado.tokens.refresh)
                    poner_cookie_dispositivo(respuesta, resultado)
        except DominioException as error:  # su `codigo` viaja a la SPA (?error_social=…)
            match error.contexto.get("proposito"):
                case Proposito.VINCULAR:
                    respuesta = a_la_spa("/acceso", error_social=error.codigo, proveedor=proveedor)
                case Proposito.REAUTENTICAR:  # módulo 92, ejercicio 3
                    respuesta = a_la_spa(error.contexto["volver"], error_social=error.codigo, proveedor=proveedor)
                case Proposito.AUTORIZAR:  # ejercicio 3: al login del authorization server, con la misma petición
                    datos = {"next": error.contexto["volver"], "error_social": error.codigo, "proveedor": proveedor}
                    respuesta = a_la_spa(LOGIN_AUTORIZACION, **datos)
                case _:
                    respuesta = a_la_spa("/login", error_social=error.codigo, proveedor=proveedor)
        return self._sin_cache(respuesta, cookie)

    def _sin_cache(self, respuesta, cookie):
        respuesta.delete_cookie(**cookie)  # gastada (la transacción ya no existe en el servidor)
        add_never_cache_headers(respuesta)
        return respuesta
