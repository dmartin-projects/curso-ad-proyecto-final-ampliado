# importaciones/infrastructure/api/v1/views/importacion_viewset.py — adapter de entrada HTTP (módulos 75 y 88)
#
# Escribir: serializer → InputDTO → use case de comando. Leer (listado, detalle, filas, la response de cada acción):
# use case de consulta → OutputDTO → presenter → el mismo serializer de siempre.
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.infrastructure.api.views import consultas
from hogares.infrastructure.api.base.del_hogar_viewset import DelHogarViewSet
from importaciones.application.confirmar_importacion_use_case.confirmar_importacion_use_case import (
    ConfirmarImportacionUseCase,
)
from importaciones.application.confirmar_importacion_use_case.dtos.confirmar_importacion_input_dto import (
    ConfirmarImportacionInputDTO,
)
from importaciones.application.deshacer_importacion_use_case.deshacer_importacion_use_case import (
    DeshacerImportacionUseCase,
)
from importaciones.application.deshacer_importacion_use_case.dtos.deshacer_importacion_input_dto import (
    DeshacerImportacionInputDTO,
)
from importaciones.application.listar_filas_importacion_use_case.dtos.listar_filas_importacion_input_dto import (
    ListarFilasImportacionInputDTO,
)
from importaciones.application.listar_importaciones_use_case.dtos.listar_importaciones_input_dto import (
    ListarImportacionesInputDTO,
)
from importaciones.application.obtener_importacion_use_case.dtos.obtener_importacion_input_dto import (
    ObtenerImportacionInputDTO,
)
from importaciones.application.subir_extracto_use_case.dtos.subir_extracto_input_dto import SubirExtractoInputDTO
from importaciones.application.subir_extracto_use_case.subir_extracto_use_case import SubirExtractoUseCase
from importaciones.infrastructure import container
from importaciones.infrastructure.api.v1.presenters.importacion_presenter import presentar, presentar_fila
from importaciones.infrastructure.api.v1.serializers.confirmar_importacion_serializer import (
    ConfirmarImportacionSerializer,
)
from importaciones.infrastructure.api.v1.serializers.fila_importacion_serializer import FilaImportacionSerializer
from importaciones.infrastructure.api.v1.serializers.importacion_serializer import ImportacionSerializer
from importaciones.infrastructure.api.v1.serializers.subir_importacion_serializer import SubirImportacionSerializer
from importaciones.infrastructure.database.models.fila_importacion_model import (
    FilaImportacion as FilaImportacionModel,
)
from importaciones.infrastructure.database.models.importacion_model import Importacion as ImportacionModel


class ImportacionViewSet(DelHogarViewSet):
    """Extractos bancarios: subir (202) → vista previa → confirmar (202) → progreso → completada."""

    modelo = ImportacionModel
    serializer_class = ImportacionSerializer
    http_method_names = ["get", "post", "head", "options"]
    filterset_fields = ["estado", "cuenta"]
    ordering = ["-creado"]
    roles_por_accion = {
        "create": SubirExtractoUseCase.rol_minimo,
        "confirmar": ConfirmarImportacionUseCase.rol_minimo,
        "deshacer": DeshacerImportacionUseCase.rol_minimo,
    }

    def get_serializer_class(self):
        return {
            "create": SubirImportacionSerializer,
            "confirmar": ConfirmarImportacionSerializer,
            "filas": FilaImportacionSerializer,
        }.get(self.action, ImportacionSerializer)

    def get_throttles(self):
        self.throttle_scope = "subidas" if self.action == "create" else None
        return super().get_throttles()

    def _leer(self, importacion_id: int):
        entrada = ObtenerImportacionInputDTO(self.hogar.pk, self.actor, importacion_id)
        leida = container.obtener_importacion().ejecutar(entrada)
        if leida is None:
            raise consultas.no_encontrado(ImportacionModel)  # el mismo 404 que get_object()
        return leida

    def _respuesta(self, importacion_id: int, codigo=status.HTTP_200_OK):
        return Response(ImportacionSerializer(presentar(self._leer(importacion_id))).data, status=codigo)

    def list(self, request, *args, **kwargs):
        filtro = consultas.filtros(consultas.filterset_de_la_view(self, ImportacionModel), request, ImportacionModel)
        datos = filtro.form.cleaned_data
        entrada = ListarImportacionesInputDTO(
            self.hogar.pk,
            self.actor,
            estado=datos.get("estado") or None,
            cuenta_id=datos["cuenta"].pk if datos.get("cuenta") else None,
            orden=consultas.orden(self, request, ImportacionModel),
            paginacion=self.paginator.paginacion(request),
        )
        pagina = container.listar_importaciones().ejecutar(entrada)
        serializados = self.get_serializer([presentar(i) for i in pagina.results], many=True).data
        return self.paginator.respuesta(request, pagina, serializados)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(presentar(self._leer(consultas.id_de_la_url(self)))).data)

    @extend_schema(responses={202: ImportacionSerializer})
    def create(self, request, *args, **kwargs):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        subida = SubirExtractoInputDTO(
            hogar_id=self.hogar.pk,
            actor=self.actor,
            cuenta_id=datos["cuenta"].pk,
            contenido=datos["archivo"],
            nombre_original=datos["archivo"].name,
            formato=datos["formato"],
            huella_archivo=datos["huella_archivo"],
        )
        return self._respuesta(container.subir_extracto().ejecutar(subida).id, status.HTTP_202_ACCEPTED)

    @extend_schema(parameters=[OpenApiParameter("accion", enum=FilaImportacionModel.Accion.values)])
    @action(detail=True, methods=["get"])
    def filas(self, request, *args, **kwargs):
        """La vista previa: cada fila con lo que se hará con ella (?accion=crear|duplicada|conciliar)."""
        entrada = ListarFilasImportacionInputDTO(
            self.hogar.pk,
            self.actor,
            consultas.id_de_la_url(self),
            request.query_params.get("accion"),
            self.paginator.paginacion(request),
        )
        pagina = container.listar_filas_importacion().ejecutar(entrada)
        if pagina is None:
            raise consultas.no_encontrado(ImportacionModel)
        datos = self.get_serializer([presentar_fila(f) for f in pagina.results], many=True).data
        return self.paginator.respuesta(request, pagina, datos)

    @extend_schema(request=ConfirmarImportacionSerializer, responses={202: ImportacionSerializer})
    @action(detail=True, methods=["post"])
    def confirmar(self, request, *args, **kwargs):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        separar = tuple(entrada.validated_data["separar"])
        importacion_id = self._leer(consultas.id_de_la_url(self)).id
        confirmacion = ConfirmarImportacionInputDTO(self.hogar.pk, self.actor, importacion_id, separar)
        return self._respuesta(container.confirmar_importacion().ejecutar(confirmacion).id, status.HTTP_202_ACCEPTED)

    @extend_schema(request=None, responses={200: ImportacionSerializer})
    @action(detail=True, methods=["post"])
    def deshacer(self, request, *args, **kwargs):
        importacion_id = self._leer(consultas.id_de_la_url(self)).id
        entrada = DeshacerImportacionInputDTO(self.hogar.pk, self.actor, importacion_id)
        return self._respuesta(container.deshacer_importacion().ejecutar(entrada).id)
