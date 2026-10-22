# backoffice/infrastructure/api/v1/views/importacion_soporte_viewset.py — adapter de entrada HTTP del personal de soporte (módulos 79 y 88)
#
# El backoffice es un adapter de entrada más: lee de TODOS los hogares con sus use cases de consulta y, para
# cambiar algo, llama a los mismos use cases que la API de los usuarios (mismas reglas, eventos y tareas) con un
# Actor.soporte: quedan registrados en la auditoría con el usuario de soporte que los hizo.
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from backoffice.application.listar_importaciones_soporte_use_case.dtos.listar_importaciones_soporte_input_dto import (
    ListarImportacionesSoporteInputDTO,
)
from backoffice.application.obtener_importacion_soporte_use_case.dtos.obtener_importacion_soporte_input_dto import (
    ObtenerImportacionSoporteInputDTO,
)
from backoffice.infrastructure import container
from backoffice.infrastructure.api.permissions.personal import PERSONAL
from backoffice.infrastructure.api.v1.presenters import soporte_presenters as presentar
from backoffice.infrastructure.api.v1.serializers.importacion_soporte_serializer import ImportacionSoporteSerializer
from backoffice.infrastructure.api.v1.views.listado_soporte_mixin import ListadoSoporteMixin
from core.domain.vo.actor import Actor
from core.infrastructure.api.views import consultas
from importaciones.application.deshacer_importacion_use_case.dtos.deshacer_importacion_input_dto import (
    DeshacerImportacionInputDTO,
)
from importaciones.domain.exceptions.estado_no_permitido_exception import (
    EstadoNoPermitidoException as ImportacionNoDeshacibleException,
)
from importaciones.infrastructure import container as importaciones
from importaciones.models import Importacion as ImportacionModel


class ImportacionSoporteViewSet(ListadoSoporteMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ImportacionSoporteSerializer
    permission_classes = PERSONAL
    permisos_por_accion = {
        "list": ["importaciones.view_importacion"],
        "retrieve": ["importaciones.view_importacion"],
        "deshacer": ["importaciones.change_importacion"],
    }
    modelo = ImportacionModel
    filtros_a_campos = {"hogar": "hogar_id"}
    filterset_fields = ["estado", "hogar"]
    search_fields = ["=id", "hogar__nombre", "nombre_original"]
    ordering = ["-creado"]

    def _leer(self, importacion_id: int):
        entrada = ObtenerImportacionSoporteInputDTO(importacion_id)
        return self._o_404(container.obtener_importacion_soporte().ejecutar(entrada))

    def list(self, request, *args, **kwargs):
        entrada = ListarImportacionesSoporteInputDTO(self._query(request))
        return self._pagina(request, container.listar_importaciones_soporte().ejecutar(entrada), presentar.importacion)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(presentar.importacion(self._leer(consultas.id_de_la_url(self)))).data)

    @extend_schema(request=None, responses=ImportacionSoporteSerializer)
    @action(detail=True, methods=["post"])
    def deshacer(self, request, *args, **kwargs):
        importacion = self._leer(consultas.id_de_la_url(self))
        entrada = DeshacerImportacionInputDTO(importacion.hogar_id, Actor.soporte(request.user.pk), importacion.id)
        try:  # el mismo use case que la API: borra con finanzas, devuelve los conciliados y audita
            importaciones.deshacer_importacion().ejecutar(entrada)
        except ImportacionNoDeshacibleException as e:
            raise ValidationError({"estado": [str(e)]}) from e
        return Response(self.get_serializer(presentar.importacion(self._leer(importacion.id))).data)
