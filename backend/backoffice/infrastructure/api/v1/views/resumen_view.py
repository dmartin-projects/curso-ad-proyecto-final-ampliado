# backoffice/infrastructure/api/v1/views/resumen_view.py — el resumen de soporte (módulos 79 y 88)
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from backoffice.application.obtener_resumen_soporte_use_case.dtos.obtener_resumen_soporte_input_dto import (
    ObtenerResumenSoporteInputDTO,
)
from backoffice.infrastructure import container
from backoffice.infrastructure.api.permissions.personal import PERSONAL
from backoffice.infrastructure.api.v1.serializers.resumen_serializer import ResumenSerializer


class ResumenView(APIView):
    """La primera pantalla de soporte: ¿va todo bien?"""

    permission_classes = PERSONAL
    permisos_por_accion = {None: ["tickets.view_ticket", "importaciones.view_importacion"]}

    @extend_schema(responses=ResumenSerializer)
    def get(self, request, *args, **kwargs):
        resumen = container.obtener_resumen_soporte().ejecutar(ObtenerResumenSoporteInputDTO())
        return Response(ResumenSerializer(resumen).data)
