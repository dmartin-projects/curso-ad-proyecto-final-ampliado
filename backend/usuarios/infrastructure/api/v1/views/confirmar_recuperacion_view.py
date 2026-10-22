# usuarios/infrastructure/api/v1/views/confirmar_recuperacion_view.py — adapter de entrada HTTP de las cuentas (módulos 35 y 88)
from rest_framework.response import Response

from usuarios.application.confirmar_recuperacion_use_case.dtos.confirmar_recuperacion_input_dto import (
    ConfirmarRecuperacionInputDTO,
)
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class ConfirmarRecuperacionView(VistaPublicaAuth):  # base de la sección 4
    def post(self, request, **kwargs):
        datos = request.data
        entrada = ConfirmarRecuperacionInputDTO(datos.get("uid", ""), datos.get("token", ""), datos.get("password", ""))
        container.confirmar_recuperacion().ejecutar(entrada)
        return Response(status=204)
