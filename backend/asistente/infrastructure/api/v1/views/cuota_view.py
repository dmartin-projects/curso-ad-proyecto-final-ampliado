# asistente/infrastructure/api/v1/views/cuota_view.py — cuánto le queda a quien pregunta (módulo 98)
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from asistente.application.consultar_cuota_use_case.dtos.consultar_cuota_input_dto import ConsultarCuotaInputDTO
from asistente.infrastructure import container
from asistente.infrastructure.api.v1.serializers.cuota_serializer import CuotaSerializer
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar
from hogares.models import Membresia


class CuotaView(HogarDesdeUrlMixin, APIView):
    """La cuota del asistente de quien pide: lo gastado hoy (suyo) y este mes (del hogar), con los límites de su plan."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    roles_por_metodo = {"GET": Membresia.Rol.LECTOR}

    @extend_schema(responses=CuotaSerializer)
    def get(self, request, hogar_pk: int, **kwargs):
        cuota = container.consultar_cuota().ejecutar(ConsultarCuotaInputDTO(self.hogar.pk, self.actor))
        return Response(CuotaSerializer(cuota).data)
