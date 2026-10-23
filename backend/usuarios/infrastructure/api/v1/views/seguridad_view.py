# usuarios/infrastructure/api/v1/views/seguridad_view.py — «Seguridad»: verificación en dos pasos y passkeys (módulo 92)
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.application.obtener_seguridad_use_case.dtos.obtener_seguridad_input_dto import ObtenerSeguridadInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.serializers.seguridad_serializer import SeguridadSerializer


class SeguridadView(APIView):
    def get(self, request, **kwargs):
        seguridad = container.obtener_seguridad().ejecutar(ObtenerSeguridadInputDTO(request.user.pk))
        return Response(SeguridadSerializer(seguridad).data)
