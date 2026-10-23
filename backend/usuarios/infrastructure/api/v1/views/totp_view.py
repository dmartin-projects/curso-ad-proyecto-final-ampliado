# usuarios/infrastructure/api/v1/views/totp_view.py — activar (empezar) y desactivar el TOTP (módulo 92)
from rest_framework.response import Response

from usuarios.application.desactivar_mfa_use_case.dtos.desactivar_mfa_input_dto import DesactivarMfaInputDTO
from usuarios.application.empezar_totp_use_case.dtos.empezar_totp_input_dto import EmpezarTotpInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.con_step_up import ConStepUp


class TotpView(ConStepUp):
    def post(self, request, **kwargs):
        """Un secreto nuevo (sin activar todavía) con su QR."""
        alta = container.empezar_totp().ejecutar(EmpezarTotpInputDTO(request.user.pk, request.user.email))
        return Response({"secreto": alta.secreto, "uri": alta.uri, "qr": alta.qr})

    def delete(self, request, **kwargs):
        container.desactivar_mfa().ejecutar(DesactivarMfaInputDTO(request.user.pk))
        return Response(status=204)
