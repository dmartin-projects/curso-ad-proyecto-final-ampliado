# usuarios/infrastructure/api/v1/views/sesion_view.py — cerrar una sesión (módulo 92)
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.application.cerrar_sesion_use_case.dtos.cerrar_sesion_input_dto import CerrarSesionInputDTO
from usuarios.infrastructure import container


class SesionView(APIView):
    def delete(self, request, sid, **kwargs):
        container.cerrar_sesion().ejecutar(CerrarSesionInputDTO(request.user.pk, str(sid)))
        return Response(status=204)
