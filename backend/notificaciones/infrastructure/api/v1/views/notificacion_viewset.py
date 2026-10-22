# notificaciones/infrastructure/api/v1/views/notificacion_viewset.py — adapter de entrada HTTP (módulos 76 y 88)
#
# Leer: use case de consulta → OutputDTO → presenter → el serializer de siempre. Marcar como leídas es CRUD
# (database/services/marcar_leidas.py): no tiene reglas ni efectos.
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.infrastructure.api.views import consultas
from notificaciones.application.contar_no_leidas_use_case.dtos.contar_no_leidas_input_dto import ContarNoLeidasInputDTO
from notificaciones.application.listar_notificaciones_use_case.dtos.listar_notificaciones_input_dto import (
    ListarNotificacionesInputDTO,
)
from notificaciones.application.obtener_notificacion_use_case.dtos.obtener_notificacion_input_dto import (
    ObtenerNotificacionInputDTO,
)
from notificaciones.infrastructure import container
from notificaciones.infrastructure.api.v1.presenters.notificacion_presenter import presentar
from notificaciones.infrastructure.api.v1.serializers.leer_serializer import LeerSerializer
from notificaciones.infrastructure.api.v1.serializers.notificacion_serializer import NotificacionSerializer
from notificaciones.infrastructure.api.v1.views.paginacion_notificaciones import PaginacionNotificaciones
from notificaciones.infrastructure.database.models.notificacion_model import Notificacion as NotificacionModel
from notificaciones.infrastructure.database.services.marcar_leidas import marcar_leidas

Contador = inline_serializer("Contador", {"no_leidas": serializers.IntegerField()})
Actualizadas = inline_serializer("Actualizadas", {"actualizadas": serializers.IntegerField()})


class NotificacionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Las notificaciones del usuario autenticado (de todos sus hogares). ?leida=false para las pendientes."""

    serializer_class = NotificacionSerializer
    pagination_class = PaginacionNotificaciones
    filterset_fields = ["leida", "tipo", "hogar"]

    def get_queryset(self):
        # El esquema OpenAPI (y la validación de ?leida, ?tipo, ?hogar) salen del modelo; los datos, del use case
        return NotificacionModel.objects.none()

    def list(self, request, *args, **kwargs):
        filtro = consultas.filtros(consultas.filterset_de_la_view(self, NotificacionModel), request, NotificacionModel)
        datos = filtro.form.cleaned_data
        entrada = ListarNotificacionesInputDTO(
            request.user.pk,
            leida=datos.get("leida"),
            tipo=datos.get("tipo") or None,
            hogar_id=datos["hogar"].pk if datos.get("hogar") else None,
            paginacion=self.paginator.paginacion(request),
        )
        pagina = container.listar_notificaciones().ejecutar(entrada)
        serializados = self.get_serializer([presentar(n) for n in pagina.results], many=True).data
        return self.paginator.respuesta(request, pagina, serializados)

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["post"])
    def leer(self, request, *args, **kwargs):
        entrada = ObtenerNotificacionInputDTO(request.user.pk, consultas.id_de_la_url(self))
        if container.obtener_notificacion().ejecutar(entrada) is None:
            raise consultas.no_encontrado(NotificacionModel)  # 404 si no es suya
        marcar_leidas(request.user.pk, [entrada.notificacion_id])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=LeerSerializer, responses={200: Actualizadas})
    @action(detail=False, methods=["post"], url_path="leer-todas")
    def leer_todas(self, request, *args, **kwargs):
        """Sin `ids`, marca todas; con `ids`, solo esas."""
        datos = LeerSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        return Response({"actualizadas": marcar_leidas(request.user.pk, datos.validated_data.get("ids"))})

    @extend_schema(responses={200: Contador})
    @action(detail=False, methods=["get"], url_path="no-leidas", filter_backends=[], pagination_class=None)
    def no_leidas(self, request, *args, **kwargs):
        return Response({"no_leidas": container.contar_no_leidas().ejecutar(ContarNoLeidasInputDTO(request.user.pk))})
