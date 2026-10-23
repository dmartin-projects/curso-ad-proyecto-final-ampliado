# usuarios/infrastructure/api/v1/views/confirmar_totp_view.py — el primer código bueno activa el MFA (módulo 92)
from rest_framework.response import Response

from usuarios.application.confirmar_totp_use_case.dtos.confirmar_totp_input_dto import ConfirmarTotpInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.con_step_up import ConStepUp


class ConfirmarTotpView(ConStepUp):
    def post(self, request, **kwargs):
        entrada = ConfirmarTotpInputDTO(request.user.pk, str(request.data.get("codigo", "")))
        codigos = container.confirmar_totp().ejecutar(entrada)
        return Response({"codigos": codigos})  # la única vez que se ven: se guardan con hash
