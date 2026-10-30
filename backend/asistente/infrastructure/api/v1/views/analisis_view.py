# asistente/infrastructure/api/v1/views/analisis_view.py — encargar el análisis del mes (módulo 105)
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from asistente.application.cancelar_analisis_use_case.dtos.cancelar_analisis_input_dto import CancelarAnalisisInputDTO
from asistente.application.pedir_analisis_use_case.dtos.pedir_analisis_input_dto import PedirAnalisisInputDTO
from asistente.infrastructure import container
from asistente.infrastructure.api.v1.serializers.analisis_serializer import (
    AnalisisPedidoSerializer,
    PedirAnalisisSerializer,
)
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar
from hogares.models import Membresia


class AnalisisView(HogarDesdeUrlMixin, APIView):
    """202 Accepted: el análisis se hace en segundo plano; el progreso y el final llegan por el WebSocket de la app
    (evento "asistente.analisis" con la `tarea`), y el informe queda como una conversación nueva."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    roles_por_metodo = {"POST": Membresia.Rol.LECTOR}
    throttle_scope = "asistente"

    @extend_schema(request=PedirAnalisisSerializer, responses={202: AnalisisPedidoSerializer})
    def post(self, request, hogar_pk: int, **kwargs):
        datos = PedirAnalisisSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        tarea = str(datos.validated_data["tarea"])
        entrada = PedirAnalisisInputDTO(self.hogar.pk, self.actor, tarea, datos.validated_data.get("mes"))
        mes = container.pedir_analisis().ejecutar(entrada)
        return Response({"tarea": tarea, "mes": mes}, status=status.HTTP_202_ACCEPTED)


class CancelarAnalisisView(HogarDesdeUrlMixin, APIView):
    """Ejercicio 1: pedir que pare. 202 también: el worker lo verá entre especialista y especialista."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    roles_por_metodo = {"DELETE": Membresia.Rol.LECTOR}

    @extend_schema(responses={202: None})
    def delete(self, request, hogar_pk: int, tarea, **kwargs):
        container.cancelar_analisis().ejecutar(CancelarAnalisisInputDTO(self.hogar.pk, self.actor, str(tarea)))
        return Response(status=status.HTTP_202_ACCEPTED)
