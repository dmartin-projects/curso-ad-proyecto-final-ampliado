# asistente/infrastructure/api/v1/views/recuerdo_viewset.py — lo que el asistente recuerda de quien pide (módulo 99)
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from asistente.application.listar_recuerdos_use_case.dtos.listar_recuerdos_input_dto import ListarRecuerdosInputDTO
from asistente.application.olvidar_recuerdo_use_case.dtos.olvidar_recuerdo_input_dto import OlvidarRecuerdoInputDTO
from asistente.infrastructure import container
from asistente.infrastructure.api.v1.serializers.recuerdo_serializer import RecuerdoSerializer
from asistente.infrastructure.api.v1.views.conversacion_viewset import TODOS
from core.infrastructure.api.views import consultas
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar


class RecuerdoViewSet(HogarDesdeUrlMixin, viewsets.ViewSet):
    """Lo que el asistente recuerda de quien pide en este hogar (lo guarda la tool `recordar`). Se ve y se borra; no se
    escribe a mano: un recuerdo es lo que se le pidió al asistente, con sus palabras."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    lookup_field, lookup_url_kwarg, lookup_value_regex = "pk", None, r"\d+"
    roles_por_metodo = TODOS
    serializer_class = RecuerdoSerializer

    @extend_schema(responses=RecuerdoSerializer(many=True))
    def list(self, request, *args, **kwargs):
        recuerdos = container.listar_recuerdos().ejecutar(ListarRecuerdosInputDTO(self.hogar.pk, self.actor))
        return Response(RecuerdoSerializer(recuerdos, many=True).data)

    def destroy(self, request, *args, **kwargs):
        entrada = OlvidarRecuerdoInputDTO(self.hogar.pk, self.actor, consultas.id_de_la_url(self))
        container.olvidar_recuerdo().ejecutar(entrada)
        return Response(status=status.HTTP_204_NO_CONTENT)
