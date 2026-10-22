# backoffice/infrastructure/api/v1/views/auditoria_viewset.py — adapter de entrada HTTP del personal de soporte (módulos 79 y 88)
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from backoffice.application.listar_auditoria_use_case.dtos.listar_auditoria_input_dto import ListarAuditoriaInputDTO
from backoffice.application.obtener_registro_auditoria_use_case.dtos.obtener_registro_auditoria_input_dto import (
    ObtenerRegistroAuditoriaInputDTO,
)
from backoffice.infrastructure import container
from backoffice.infrastructure.api.permissions.personal import PERSONAL
from backoffice.infrastructure.api.v1.presenters import soporte_presenters as presentar
from backoffice.infrastructure.api.v1.serializers.auditoria_serializer import AuditoriaSerializer
from backoffice.infrastructure.api.v1.views.listado_soporte_mixin import ListadoSoporteMixin
from core.infrastructure.api.views import consultas
from core.models import RegistroAuditoria as RegistroAuditoriaModel


class AuditoriaViewSet(ListadoSoporteMixin, viewsets.ReadOnlyModelViewSet):
    """Solo lectura, también para el superusuario: una auditoría que se puede editar no sirve."""

    serializer_class = AuditoriaSerializer
    permission_classes = PERSONAL
    permisos_por_accion = {"list": ["core.view_registroauditoria"], "retrieve": ["core.view_registroauditoria"]}
    modelo = RegistroAuditoriaModel
    filterset_fields = ["accion", "object_id"]
    search_fields = ["representacion", "usuario__email"]

    @extend_schema(parameters=[OpenApiParameter("modelo", str, description="app.modelo, p. ej. finanzas.movimiento")])
    def list(self, request, *args, **kwargs):
        entrada = ListarAuditoriaInputDTO(self._query(request), request.query_params.get("modelo"))
        return self._pagina(request, container.listar_auditoria().ejecutar(entrada), presentar.registro)

    def retrieve(self, request, *args, **kwargs):
        entrada = ObtenerRegistroAuditoriaInputDTO(consultas.id_de_la_url(self))
        leido = self._o_404(container.obtener_registro_auditoria().ejecutar(entrada))
        return Response(self.get_serializer(presentar.registro(leido)).data)
