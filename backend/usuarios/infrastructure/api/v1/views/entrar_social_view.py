# usuarios/infrastructure/api/v1/views/entrar_social_view.py — la ida al proveedor desde el login (módulo 91)
from django.http import HttpResponseRedirect

from core.domain.exceptions.dominio_exception import DominioException
from usuarios.application.empezar_login_social_use_case.dtos.empezar_login_social_input_dto import (
    EmpezarLoginSocialInputDTO,
)
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.a_la_spa import a_la_spa
from usuarios.infrastructure.api.v1.views.cookie_social import recordar
from usuarios.infrastructure.api.v1.views.rutas_autorizacion import AUTORIZAR, LOGIN_AUTORIZACION
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class EntrarSocialView(VistaPublicaAuth):
    """GET /social/<proveedor>/entrar/?volver=/hogares/3: un enlace del login de la SPA. Redirige al proveedor."""

    throttle_scope = "social"

    def get(self, request, proveedor, **kwargs):
        volver, proposito = request.query_params.get("volver", ""), Proposito.ENTRAR
        if request.query_params.get("para") == "autorizar":  # ejercicio 3: desde el login del authorization server
            proposito = Proposito.AUTORIZAR
            volver = volver if volver.startswith(AUTORIZAR) else LOGIN_AUTORIZACION
        try:
            entrada = EmpezarLoginSocialInputDTO(Proveedor.de(proveedor), proposito, volver=volver or None)
            ida = container.empezar_login_social().ejecutar(entrada)
        except DominioException as error:
            return a_la_spa("/login", error_social=error.codigo, proveedor=proveedor)
        respuesta = HttpResponseRedirect(ida.url)
        recordar(respuesta, entrada.proveedor, ida)
        return respuesta
