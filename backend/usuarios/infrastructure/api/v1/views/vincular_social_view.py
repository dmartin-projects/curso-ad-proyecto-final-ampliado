# usuarios/infrastructure/api/v1/views/vincular_social_view.py — la ida al proveedor para vincularlo (módulos 91 y 92)
from rest_framework.response import Response

from usuarios.application.empezar_login_social_use_case.dtos.empezar_login_social_input_dto import (
    EmpezarLoginSocialInputDTO,
)
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.con_step_up import ConStepUp
from usuarios.infrastructure.api.v1.views.cookie_social import recordar


class VincularSocialView(ConStepUp):
    """POST con el JWT de la SPA: la URL del proveedor para vincularlo a MI cuenta. La SPA navega a ella. Añade una
    forma de entrar: es una acción sensible."""

    throttle_scope = "social"

    def post(self, request, proveedor, **kwargs):
        entrada = EmpezarLoginSocialInputDTO(Proveedor.de(proveedor), Proposito.VINCULAR, usuario_id=request.user.pk)
        ida = container.empezar_login_social().ejecutar(entrada)
        respuesta = Response({"url": ida.url})
        recordar(respuesta, entrada.proveedor, ida)
        return respuesta
