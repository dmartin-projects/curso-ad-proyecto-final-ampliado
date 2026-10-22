# usuarios/infrastructure/api/v1/views/solicitar_recuperacion_view.py — adapter de entrada HTTP de las cuentas (módulos 35 y 88)
from rest_framework.response import Response

from usuarios.application.solicitar_recuperacion_use_case.dtos.solicitar_recuperacion_input_dto import (
    SolicitarRecuperacionInputDTO,
)
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class SolicitarRecuperacionView(VistaPublicaAuth):  # base de la sección 4
    throttle_scope = "recuperar"

    def post(self, request, **kwargs):
        container.solicitar_recuperacion().ejecutar(SolicitarRecuperacionInputDTO(request.data.get("email", "")))
        # 🔐 misma respuesta exista o no: no reveles qué emails están registrados
        return Response({"detail": "Si el email existe, te hemos enviado un enlace."})
