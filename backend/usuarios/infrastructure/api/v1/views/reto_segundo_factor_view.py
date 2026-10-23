# usuarios/infrastructure/api/v1/views/reto_segundo_factor_view.py — una passkey como segundo factor (módulo 92)
from rest_framework.response import Response

from usuarios.application.obtener_login_pendiente_use_case.dtos.obtener_login_pendiente_input_dto import (
    ObtenerLoginPendienteInputDTO,
)
from usuarios.application.pedir_reto_use_case.dtos.pedir_reto_input_dto import PedirRetoInputDTO
from usuarios.domain.enums.canal import Canal
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.cookie_mfa import COOKIE_MFA
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class RetoSegundoFactorView(VistaPublicaAuth):
    """Las opciones de WebAuthn para usar una passkey como segundo factor: solo las de esa cuenta."""

    throttle_scope = "mfa"

    def post(self, request, **kwargs):
        clave = request.COOKIES.get(COOKIE_MFA)
        pendiente = container.obtener_login_pendiente().ejecutar(ObtenerLoginPendienteInputDTO(clave, Canal.SPA))
        return Response(container.pedir_reto().ejecutar(PedirRetoInputDTO(f"segundo:{clave}", pendiente.usuario_id)))
