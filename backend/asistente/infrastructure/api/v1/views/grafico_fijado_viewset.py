# asistente/infrastructure/api/v1/views/grafico_fijado_viewset.py — los gráficos del dashboard del hogar (módulo 97)
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from asistente.application.fijar_grafico_use_case.dtos.fijar_grafico_input_dto import FijarGraficoInputDTO
from asistente.application.fijar_grafico_use_case.fijar_grafico_use_case import FijarGraficoUseCase
from asistente.application.listar_graficos_fijados_use_case.dtos.listar_graficos_fijados_input_dto import (
    ListarGraficosFijadosInputDTO,
)
from asistente.application.quitar_grafico_use_case.dtos.quitar_grafico_input_dto import QuitarGraficoInputDTO
from asistente.application.quitar_grafico_use_case.quitar_grafico_use_case import QuitarGraficoUseCase
from asistente.infrastructure import container
from asistente.infrastructure.api.v1.serializers.grafico_fijado_serializer import (
    EspecificacionSerializer,
    GraficoFijadoSerializer,
)
from core.infrastructure.api.views import consultas
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar
from hogares.models import Membresia


class GraficoFijadoViewSet(HogarDesdeUrlMixin, viewsets.ViewSet):
    """Los gráficos del chat fijados en el dashboard del hogar, recalculados al pedirlos."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    lookup_field, lookup_url_kwarg, lookup_value_regex = "pk", None, r"\d+"
    roles_por_metodo = {"GET": Membresia.Rol.LECTOR}
    roles_por_accion = {"create": FijarGraficoUseCase.rol_minimo, "destroy": QuitarGraficoUseCase.rol_minimo}
    serializer_class = GraficoFijadoSerializer

    @extend_schema(responses=GraficoFijadoSerializer(many=True))
    def list(self, request, *args, **kwargs):
        graficos = container.listar_graficos_fijados().ejecutar(
            ListarGraficosFijadosInputDTO(self.hogar.pk, self.actor)
        )
        return Response(GraficoFijadoSerializer(graficos, many=True).data)

    @extend_schema(request=EspecificacionSerializer, responses={201: GraficoFijadoSerializer})
    def create(self, request, *args, **kwargs):
        datos = EspecificacionSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        fijado = container.fijar_grafico().ejecutar(
            FijarGraficoInputDTO(self.hogar.pk, self.actor, dict(datos.validated_data))
        )
        return Response(GraficoFijadoSerializer(fijado).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        container.quitar_grafico().ejecutar(
            QuitarGraficoInputDTO(self.hogar.pk, self.actor, consultas.id_de_la_url(self))
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
