# usuarios/infrastructure/api/v1/views/reto_registro_passkey_view.py — las opciones para crear una passkey (módulo 92)
from rest_framework.response import Response

from usuarios.application.empezar_registro_passkey_use_case.dtos.empezar_registro_passkey_input_dto import (
    EmpezarRegistroPasskeyInputDTO,
)
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.con_step_up import ConStepUp


class RetoRegistroPasskeyView(ConStepUp):
    def post(self, request, **kwargs):
        usuario = request.user
        entrada = EmpezarRegistroPasskeyInputDTO(usuario.pk, usuario.email, usuario.get_full_name())
        return Response(container.empezar_registro_passkey().ejecutar(entrada))
