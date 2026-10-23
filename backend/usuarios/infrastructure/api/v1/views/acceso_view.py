# usuarios/infrastructure/api/v1/views/acceso_view.py — «Métodos de acceso» (módulo 91)
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.application.obtener_acceso_use_case.dtos.obtener_acceso_input_dto import ObtenerAccesoInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.serializers.acceso_serializer import AccesoSerializer


class AccesoView(APIView):
    """Las formas de entrar de mi cuenta: la contraseña (si tiene) y los proveedores vinculados."""

    def get(self, request, **kwargs):
        acceso = container.obtener_acceso().ejecutar(ObtenerAccesoInputDTO(request.user.pk))
        return Response(AccesoSerializer(acceso).data)
