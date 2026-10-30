# asistente/infrastructure/api/v1/views/propuesta_viewset.py — confirmar o descartar lo que propone el asistente (módulo 97)
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from asistente.application.confirmar_propuesta_use_case.dtos.confirmar_propuesta_input_dto import (
    ConfirmarPropuestaInputDTO,
)
from asistente.application.descartar_propuesta_use_case.dtos.descartar_propuesta_input_dto import (
    DescartarPropuestaInputDTO,
)
from asistente.infrastructure import container
from asistente.infrastructure.api.v1.serializers.propuesta_serializer import PropuestaSerializer
from asistente.infrastructure.api.v1.views.conversacion_viewset import TODOS
from core.infrastructure.api.views import consultas
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar


class PropuestaViewSet(HogarDesdeUrlMixin, viewsets.ViewSet):
    """Sin listado ni detalle: las propuestas se ven dentro de su conversación. Aquí solo se resuelven.

    El rol no se mira aquí: confirmar ejecuta el use case de la app dueña con el Actor de quien confirma, y ESE use
    case exige su rol (registrar un movimiento: miembro). Un lector recibe el mismo 403 que en el formulario."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    lookup_field, lookup_url_kwarg, lookup_value_regex = "pk", None, r"\d+"
    roles_por_metodo = TODOS
    serializer_class = PropuestaSerializer

    @extend_schema(request=None, responses=PropuestaSerializer)
    @action(detail=True, methods=["post"])
    def confirmar(self, request, *args, **kwargs):
        entrada = ConfirmarPropuestaInputDTO(self.hogar.pk, self.actor, consultas.id_de_la_url(self))
        return Response(PropuestaSerializer(container.confirmar_propuesta().ejecutar(entrada)).data)

    @extend_schema(request=None, responses=PropuestaSerializer)
    @action(detail=True, methods=["post"])
    def descartar(self, request, *args, **kwargs):
        entrada = DescartarPropuestaInputDTO(self.hogar.pk, self.actor, consultas.id_de_la_url(self))
        return Response(PropuestaSerializer(container.descartar_propuesta().ejecutar(entrada)).data)
