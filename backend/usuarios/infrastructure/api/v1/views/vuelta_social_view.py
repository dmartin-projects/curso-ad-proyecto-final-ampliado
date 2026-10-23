# usuarios/infrastructure/api/v1/views/vuelta_social_view.py — la vuelta del proveedor (módulo 91)
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
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.a_la_spa import a_la_spa
from usuarios.infrastructure.api.v1.views.cookie_refresh import poner_cookie_refresh
from usuarios.infrastructure.api.v1.views.cookie_social import cookie_social
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
            else:
                # Los MISMOS tokens que con la contraseña: el refresh, en su cookie; el access lo pide la SPA al
                # arrancar (POST /auth/refresh/, como tras un F5). Los del proveedor ni se guardan ni llegan aquí
                sesion = container.iniciar_sesion().ejecutar(IniciarSesionInputDTO(hecho.usuario_id))
                respuesta = a_la_spa(hecho.volver)
                poner_cookie_refresh(respuesta, sesion.refresh)
        except DominioException as error:  # su `codigo` viaja a la SPA (?error_social=…)
            pagina = "/acceso" if error.contexto.get("proposito") is Proposito.VINCULAR else "/login"
            respuesta = a_la_spa(pagina, error_social=error.codigo, proveedor=proveedor)
        respuesta.delete_cookie(**cookie)  # gastada (la transacción ya no existe en el servidor)
        add_never_cache_headers(respuesta)
        return respuesta
