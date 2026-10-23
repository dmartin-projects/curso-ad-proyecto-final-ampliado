# usuarios/infrastructure/api/v1/views/segundo_factor_view.py — el segundo paso del login (módulo 92)
from rest_framework.response import Response

from usuarios.application.completar_segundo_factor_use_case.dtos.completar_segundo_factor_input_dto import (
    CompletarSegundoFactorInputDTO,
)
from usuarios.application.obtener_factores_use_case.dtos.obtener_factores_input_dto import ObtenerFactoresInputDTO
from usuarios.application.obtener_login_pendiente_use_case.dtos.obtener_login_pendiente_input_dto import (
    ObtenerLoginPendienteInputDTO,
)
from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.factor import Factor
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import contexto_de
from usuarios.infrastructure.api.v1.serializers.segundo_factor_serializer import SegundoFactorSerializer
from usuarios.infrastructure.api.v1.views.cookie_mfa import COOKIE_MFA
from usuarios.infrastructure.api.v1.views.responder import responder
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class SegundoFactorView(VistaPublicaAuth):
    """GET: con qué se puede completar (la pantalla de la SPA tras volver de un proveedor). POST: completarlo."""

    throttle_scope = "mfa"

    def _clave(self, request):
        return request.COOKIES.get(COOKIE_MFA)

    def get(self, request, **kwargs):
        pendiente = container.obtener_login_pendiente().ejecutar(
            ObtenerLoginPendienteInputDTO(self._clave(request), Canal.SPA)
        )
        factores = container.obtener_factores().ejecutar(ObtenerFactoresInputDTO(pendiente.usuario_id))
        return Response({"factores": factores.segundos})

    def post(self, request, **kwargs):
        datos = SegundoFactorSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        entrada = CompletarSegundoFactorInputDTO(
            self._clave(request), Canal.SPA, Factor(datos.validated_data["factor"]),
            datos.validated_data.get("codigo", ""), datos.validated_data.get("respuesta"), contexto_de(request),
        )  # fmt: skip
        sesion, _ = container.completar_segundo_factor().ejecutar(entrada)
        return responder(sesion)
