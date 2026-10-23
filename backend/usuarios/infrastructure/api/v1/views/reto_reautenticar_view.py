# usuarios/infrastructure/api/v1/views/reto_reautenticar_view.py — una passkey para el step-up (módulo 92)
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.application.pedir_reto_use_case.dtos.pedir_reto_input_dto import PedirRetoInputDTO
from usuarios.infrastructure import container


class RetoReautenticarView(APIView):
    throttle_scope = "mfa"

    def post(self, request, **kwargs):
        usuario_id = request.user.pk
        return Response(container.pedir_reto().ejecutar(PedirRetoInputDTO(f"reautenticar:{usuario_id}", usuario_id)))
