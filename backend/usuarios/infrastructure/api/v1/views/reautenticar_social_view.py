# usuarios/infrastructure/api/v1/views/reautenticar_social_view.py — el step-up con el proveedor (módulo 92, ej. 3)
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.application.empezar_login_social_use_case.dtos.empezar_login_social_input_dto import (
    EmpezarLoginSocialInputDTO,
)
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.sesion_cerrada_exception import SesionCerradaException
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import sid_de
from usuarios.infrastructure.api.v1.views.cookie_social import recordar


class ReautenticarSocialView(APIView):
    """Módulo 92, ejercicio 3: POST con el JWT de la SPA: la URL del proveedor para confirmar quién eres (step-up de una
    cuenta sin contraseña). A la vuelta, la sesión de este JWT queda reautenticada y se vuelve a `volver`."""

    throttle_scope = "social"

    def post(self, request, proveedor, **kwargs):
        entrada = EmpezarLoginSocialInputDTO(
            Proveedor.de(proveedor), Proposito.REAUTENTICAR, volver=str(request.data.get("volver") or "/"),
            usuario_id=request.user.pk, sid=sid_de(request),
        )  # fmt: skip
        if not entrada.sid:
            raise SesionCerradaException()
        ida = container.empezar_login_social().ejecutar(entrada)
        respuesta = Response({"url": ida.url})
        recordar(respuesta, entrada.proveedor, ida)
        return respuesta
