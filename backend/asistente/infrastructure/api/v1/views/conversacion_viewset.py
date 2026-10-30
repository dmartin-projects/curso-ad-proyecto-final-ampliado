# asistente/infrastructure/api/v1/views/conversacion_viewset.py — las conversaciones de quien pregunta (módulo 97)
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from asistente.application.crear_conversacion_use_case.dtos.crear_conversacion_input_dto import (
    CrearConversacionInputDTO,
)
from asistente.application.eliminar_conversacion_use_case.dtos.eliminar_conversacion_input_dto import (
    EliminarConversacionInputDTO,
)
from asistente.application.listar_conversaciones_use_case.dtos.listar_conversaciones_input_dto import (
    ListarConversacionesInputDTO,
)
from asistente.application.modificar_conversacion_use_case.dtos.modificar_conversacion_input_dto import (
    ModificarConversacionInputDTO,
)
from asistente.application.obtener_conversacion_use_case.dtos.obtener_conversacion_input_dto import (
    ObtenerConversacionInputDTO,
)
from asistente.infrastructure import container
from asistente.infrastructure.api.v1.serializers.conversacion_detalle_serializer import ConversacionDetalleSerializer
from asistente.infrastructure.api.v1.serializers.conversacion_serializer import ConversacionSerializer
from asistente.infrastructure.database.models.conversacion_model import Conversacion as ConversacionModel
from core.infrastructure.api.views import consultas
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar
from hogares.models import Membresia

TODOS = {m: Membresia.Rol.LECTOR for m in ("GET", "POST", "PATCH", "DELETE")}  # son de cada persona: su rol no limita


class ConversacionViewSet(HogarDesdeUrlMixin, viewsets.ViewSet):
    """Las conversaciones con el asistente de quien pide, en este hogar (las de los demás miembros no se ven)."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    lookup_field, lookup_url_kwarg, lookup_value_regex = "pk", None, r"\d+"
    roles_por_metodo = TODOS
    serializer_class = ConversacionSerializer

    def _leer(self, conversacion_id: int):
        leida = container.obtener_conversacion().ejecutar(
            ObtenerConversacionInputDTO(self.hogar.pk, self.actor, conversacion_id)
        )
        if leida is None:
            raise consultas.no_encontrado(ConversacionModel)
        return leida

    @extend_schema(
        parameters=[OpenApiParameter("carpeta", int, description="Solo las de esa carpeta")],
        responses=ConversacionSerializer(many=True),
    )
    def list(self, request, *args, **kwargs):
        carpeta = request.query_params.get("carpeta")
        if carpeta is not None and not carpeta.isdigit():
            raise ValidationError({"carpeta": ["Un número entero."]})
        entrada = ListarConversacionesInputDTO(self.hogar.pk, self.actor, int(carpeta) if carpeta else None)
        return Response(ConversacionSerializer(container.listar_conversaciones().ejecutar(entrada), many=True).data)

    @extend_schema(request=ConversacionSerializer, responses={201: ConversacionDetalleSerializer})
    def create(self, request, *args, **kwargs):
        datos = ConversacionSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        entrada = CrearConversacionInputDTO(self.hogar.pk, self.actor, datos.validated_data.get("carpeta_id"))
        creada = container.crear_conversacion().ejecutar(entrada)
        return Response(ConversacionDetalleSerializer(self._leer(creada.id)).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=ConversacionDetalleSerializer)
    def retrieve(self, request, *args, **kwargs):
        return Response(ConversacionDetalleSerializer(self._leer(consultas.id_de_la_url(self))).data)

    @extend_schema(request=ConversacionSerializer, responses=ConversacionDetalleSerializer)
    def partial_update(self, request, *args, **kwargs):
        datos = ConversacionSerializer(data=request.data, partial=True)
        datos.is_valid(raise_exception=True)
        conversacion_id = consultas.id_de_la_url(self)
        entrada = ModificarConversacionInputDTO(self.hogar.pk, self.actor, conversacion_id, datos.a_dominio())
        container.modificar_conversacion().ejecutar(entrada)
        return Response(ConversacionDetalleSerializer(self._leer(conversacion_id)).data)

    def destroy(self, request, *args, **kwargs):
        entrada = EliminarConversacionInputDTO(self.hogar.pk, self.actor, consultas.id_de_la_url(self))
        container.eliminar_conversacion().ejecutar(entrada)
        return Response(status=status.HTTP_204_NO_CONTENT)
