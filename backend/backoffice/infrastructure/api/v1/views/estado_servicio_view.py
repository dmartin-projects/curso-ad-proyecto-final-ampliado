# backoffice/infrastructure/api/v1/views/estado_servicio_view.py — el resumen, para un servicio de monitorización (módulo 90)
#
# Sin persona detrás: un token de client credentials con el scope operaciones:leer. Ni el JWT de la SPA (tampoco el
# del personal) ni los tokens de un usuario sirven aquí.
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from backoffice.application.obtener_resumen_soporte_use_case.dtos.obtener_resumen_soporte_input_dto import (
    ObtenerResumenSoporteInputDTO,
)
from backoffice.infrastructure import container
from backoffice.infrastructure.api.v1.serializers.resumen_serializer import ResumenSerializer
from oauth.domain.enums.scope import Scope
from oauth.infrastructure.api.authentication.autenticacion_oauth import AutenticacionOAuth
from oauth.infrastructure.api.permissions.es_servicio import EsServicio
from oauth.infrastructure.api.permissions.scope_requerido import ScopeRequerido


class EstadoServicioView(APIView):
    """Estado de las colas y los procesos, para un servicio de monitorización (OAuth: client credentials)."""

    authentication_classes = [AutenticacionOAuth]
    permission_classes = [EsServicio, ScopeRequerido]
    scopes_por_accion = {None: Scope.OPERACIONES_LEER}

    @extend_schema(responses=ResumenSerializer)
    def get(self, request, *args, **kwargs):
        resumen = container.obtener_resumen_soporte().ejecutar(ObtenerResumenSoporteInputDTO())
        return Response(ResumenSerializer(resumen).data)
