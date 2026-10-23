# usuarios/infrastructure/api/v1/views/passkey_view.py — quitar una passkey (módulo 92)
from rest_framework.response import Response

from usuarios.application.borrar_passkey_use_case.dtos.borrar_passkey_input_dto import BorrarPasskeyInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.con_step_up import ConStepUp


class PasskeyView(ConStepUp):
    def delete(self, request, passkey_id, **kwargs):
        container.borrar_passkey().ejecutar(BorrarPasskeyInputDTO(request.user.pk, passkey_id))
        return Response(status=204)
