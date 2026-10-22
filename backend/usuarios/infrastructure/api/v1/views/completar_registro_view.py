# usuarios/infrastructure/api/v1/views/completar_registro_view.py — adapter de entrada HTTP de las cuentas (módulos 35 y 88)
from rest_framework.response import Response

from usuarios.application.completar_registro_use_case.dtos.completar_registro_input_dto import CompletarRegistroInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class CompletarRegistroView(VistaPublicaAuth):  # base de la sección 4
    def post(self, request, **kwargs):
        datos = request.data
        entrada = CompletarRegistroInputDTO(datos.get("uid", ""), datos.get("token", ""), datos.get("password", ""))
        container.completar_registro().ejecutar(entrada)
        return Response(status=204)
