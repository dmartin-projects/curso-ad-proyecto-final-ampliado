# finanzas/infrastructure/api/v1/views/dashboard_view.py — adapter de entrada HTTP (módulos 23, 77 y 87)
from zoneinfo import ZoneInfo

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes
from finanzas.application.obtener_dashboard_use_case.dtos.obtener_dashboard_input_dto import ObtenerDashboardInputDTO
from finanzas.infrastructure import container
from finanzas.infrastructure.api.v1.serializers.dashboard_serializer import DashboardSerializer
from finanzas.infrastructure.api.v1.serializers.mes_query_serializer import MesQuerySerializer
from finanzas.infrastructure.cache import dashboard_cache
from hogares.permissions import HogarDesdeUrlMixin, RolEnHogar


def mes_actual(hogar) -> Mes:
    """El mes "de hoy" en la zona horaria del hogar: a las 00:30 del día 1 en Madrid aún es el mes anterior en UTC."""
    return Mes.de(timezone.localdate(timezone=ZoneInfo(hogar.zona_horaria)))


class DashboardView(HogarDesdeUrlMixin, APIView):
    """Resumen del mes. Cacheado por hogar y versión; responde 304 si el cliente ya tiene la versión actual."""

    permission_classes = [IsAuthenticated, RolEnHogar]  # GET → lector

    @extend_schema(parameters=[MesQuerySerializer], responses={200: DashboardSerializer, 304: None})
    def get(self, request, *args, **kwargs):
        consulta = MesQuerySerializer(data=request.query_params)
        consulta.is_valid(raise_exception=True)
        fecha = consulta.validated_data.get("mes")
        mes = Mes.de(fecha) if fecha else mes_actual(self.hogar)

        # ETag barato: no hace falta calcular nada para saber si el cliente ya lo tiene (módulo 23)
        etag = f'"dashboard-{self.hogar.pk}-v{dashboard_cache.version(self.hogar.pk)}-{mes}"'
        cabeceras = {"ETag": etag, "Cache-Control": "private, no-cache"}  # el navegador guarda, pero pregunta
        if etag in request.headers.get("If-None-Match", ""):
            return Response(status=status.HTTP_304_NOT_MODIFIED, headers=cabeceras)

        actor = Actor(usuario_id=request.user.pk, rol=Rol(self.membresia.rol))
        datos = container.obtener_dashboard().ejecutar(ObtenerDashboardInputDTO(self.hogar.pk, actor, mes))
        return Response(DashboardSerializer(datos).data, headers=cabeceras)
