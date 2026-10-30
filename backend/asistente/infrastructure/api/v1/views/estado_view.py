# asistente/infrastructure/api/v1/views/estado_view.py — si el asistente está disponible (módulo 107)
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from asistente.application.obtener_estado_use_case.dtos.obtener_estado_input_dto import ObtenerEstadoInputDTO
from asistente.infrastructure import container
from asistente.infrastructure.api.v1.serializers.estado_serializer import EstadoDelAsistenteSerializer
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar
from hogares.models import Membresia


class EstadoView(HogarDesdeUrlMixin, APIView):
    permission_classes = [IsAuthenticated, RolEnHogar]
    roles_por_metodo = {"GET": Membresia.Rol.LECTOR}

    @extend_schema(responses=EstadoDelAsistenteSerializer)
    def get(self, request, hogar_pk: int, **kwargs):
        estado = container.obtener_estado().ejecutar(ObtenerEstadoInputDTO(self.hogar.pk, self.actor))
        return Response(EstadoDelAsistenteSerializer(estado).data)
