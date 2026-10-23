# usuarios/infrastructure/api/v1/views/sesiones_view.py — las sesiones abiertas de mi cuenta (módulo 92)
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.application.listar_sesiones_use_case.dtos.listar_sesiones_input_dto import ListarSesionesInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import sid_de
from usuarios.infrastructure.api.v1.serializers.sesion_activa_serializer import SesionActivaSerializer


class SesionesView(APIView):
    def get(self, request, **kwargs):
        sesiones = container.listar_sesiones().ejecutar(ListarSesionesInputDTO(request.user.pk, sid_de(request)))
        return Response(SesionActivaSerializer(sesiones, many=True).data)
