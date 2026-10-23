# usuarios/infrastructure/api/v1/views/cerrar_las_demas_view.py — cerrar todas las sesiones menos esta (módulo 92)
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.application.cerrar_las_demas_use_case.dtos.cerrar_las_demas_input_dto import CerrarLasDemasInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import sid_de


class CerrarLasDemasView(APIView):
    def post(self, request, **kwargs):
        cerradas = container.cerrar_las_demas().ejecutar(CerrarLasDemasInputDTO(request.user.pk, sid_de(request) or ""))
        return Response({"cerradas": cerradas})
