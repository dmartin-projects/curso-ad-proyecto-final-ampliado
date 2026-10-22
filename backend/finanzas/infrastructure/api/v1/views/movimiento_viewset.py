# finanzas/infrastructure/api/v1/views/movimiento_viewset.py — adapter de entrada HTTP (módulos 33-38, 76, 87 y 88)
#
# Escribir: serializer → InputDTO → use case de comando. Leer (listado, detalle, CSV y la response de un POST o un
# PATCH): query params → InputDTO → use case de consulta → OutputDTO → presenter → el mismo serializer de siempre.
import csv

from django.http import StreamingHttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from core.infrastructure.api.pagination.paginacion_cursor import PaginacionCursor
from core.infrastructure.api.pagination.paginacion_estandar import PaginacionEstandar
from core.infrastructure.api.views import consultas
from core.infrastructure.api.views.roles import roles_de
from core.infrastructure.hojas_de_calculo.celdas_de_texto import texto_csv
from finanzas.application.eliminar_movimiento_use_case.dtos.eliminar_movimiento_input_dto import (
    EliminarMovimientoInputDTO,
)
from finanzas.application.eliminar_movimiento_use_case.eliminar_movimiento_use_case import EliminarMovimientoUseCase
from finanzas.application.exportar_movimientos_use_case.dtos.exportar_movimientos_input_dto import (
    ExportarMovimientosInputDTO,
)
from finanzas.application.listar_movimientos_use_case.dtos.listar_movimientos_input_dto import (
    ListarMovimientosInputDTO,
)
from finanzas.application.modificar_movimiento_use_case.dtos.modificar_movimiento_input_dto import (
    ModificarMovimientoInputDTO,
)
from finanzas.application.modificar_movimiento_use_case.modificar_movimiento_use_case import (
    ModificarMovimientoUseCase,
)
from finanzas.application.obtener_movimiento_use_case.dtos.obtener_movimiento_input_dto import (
    ObtenerMovimientoInputDTO,
)
from finanzas.application.recategorizar_movimientos_use_case.dtos.recategorizar_movimientos_input_dto import (
    RecategorizarMovimientosInputDTO,
)
from finanzas.application.recategorizar_movimientos_use_case.recategorizar_movimientos_use_case import (
    RecategorizarMovimientosUseCase,
)
from finanzas.application.registrar_movimiento_use_case.dtos.registrar_movimiento_input_dto import (
    RegistrarMovimientoInputDTO,
)
from finanzas.application.registrar_movimiento_use_case.registrar_movimiento_use_case import (
    RegistrarMovimientoUseCase,
)
from finanzas.infrastructure import container
from finanzas.infrastructure.api.v1.filters.movimiento_filter import MovimientoFilter
from finanzas.infrastructure.api.v1.presenters.movimiento_presenter import presentar
from finanzas.infrastructure.api.v1.serializers.movimiento_serializer import MovimientoSerializer
from finanzas.infrastructure.api.v1.serializers.recategorizar_serializer import RecategorizarSerializer
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel
from hogares.infrastructure.api.base.del_hogar_viewset import DelHogarViewSet


class MovimientoViewSet(DelHogarViewSet):
    # Estos atributos son los de siempre: de ellos salen el esquema OpenAPI (filtros, búsqueda, orden, paginación)
    # y la validación de los query params. El QuerySet de DelHogarViewSet solo lo usa get_object() al modificar.
    modelo = MovimientoModel
    serializer_class = MovimientoSerializer
    filterset_class = MovimientoFilter
    search_fields = ["concepto", "comercio__nombre", "notas"]
    ordering_fields = ["fecha", "importe", "concepto"]
    ordering = ["-fecha", "-id"]
    pagination_class = PaginacionCursor
    roles_por_accion = roles_de(RegistrarMovimientoUseCase, ModificarMovimientoUseCase, EliminarMovimientoUseCase) | {
        "recategorizar": RecategorizarMovimientosUseCase.rol_minimo
    }

    @property
    def paginator(self):
        # El cursor necesita un orden fijo: si el usuario ordena por importe, paginación normal (módulo 37)
        if not hasattr(self, "_paginator"):
            ordenado = self.request.query_params.get("ordering") if hasattr(self, "request") else None
            self._paginator = PaginacionEstandar() if ordenado else PaginacionCursor()
        return self._paginator

    def _filtros_y_orden(self, request):
        filtros = consultas.filtros(MovimientoFilter, request, MovimientoModel).a_dominio(consultas.busqueda(request))
        return filtros, consultas.orden(self, request, MovimientoModel)

    def _leer(self, movimiento_id: int):
        leido = container.obtener_movimiento().ejecutar(
            ObtenerMovimientoInputDTO(self.hogar.pk, self.actor, movimiento_id)
        )
        if leido is None:
            raise consultas.no_encontrado(MovimientoModel)
        return presentar(leido)

    def list(self, request, *args, **kwargs):
        filtros, orden = self._filtros_y_orden(request)
        entrada = ListarMovimientosInputDTO(
            self.hogar.pk, self.actor, filtros, orden, self.paginator.paginacion(request)
        )
        pagina = container.listar_movimientos().ejecutar(entrada)
        datos = self.get_serializer([presentar(m) for m in pagina.results], many=True).data
        return self.paginator.respuesta(request, pagina, datos)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self._leer(consultas.id_de_la_url(self))).data)

    def perform_create(self, serializer):
        entrada = RegistrarMovimientoInputDTO(hogar_id=self.hogar.pk, actor=self.actor, **serializer.a_dominio())
        movimiento = container.registrar_movimiento().ejecutar(entrada)
        serializer.instance = self._leer(movimiento.id)  # la response: el lado de lectura

    def perform_update(self, serializer):
        entrada = ModificarMovimientoInputDTO(self.hogar.pk, self.actor, serializer.instance.pk, serializer.a_dominio())
        container.modificar_movimiento().ejecutar(entrada)
        serializer.instance = self._leer(serializer.instance.pk)

    def perform_destroy(self, instance):
        container.eliminar_movimiento().ejecutar(EliminarMovimientoInputDTO(self.hogar.pk, self.actor, instance.pk))

    @extend_schema(
        request=RecategorizarSerializer,
        responses={200: {"type": "object", "properties": {"actualizados": {"type": "integer"}}}},
    )
    @action(detail=False, methods=["post"])
    def recategorizar(self, request, *args, **kwargs):
        datos = RecategorizarSerializer(data=request.data, context=self.get_serializer_context())
        datos.is_valid(raise_exception=True)
        entrada = RecategorizarMovimientosInputDTO(
            self.hogar.pk, self.actor, tuple(datos.validated_data["ids"]), datos.validated_data["categoria"].pk
        )
        return Response({"actualizados": container.recategorizar_movimientos().ejecutar(entrada)})

    @extend_schema(responses={(200, "text/csv"): str})
    @action(detail=False, methods=["get"])
    def exportar(self, request, *args, **kwargs):
        filtros, orden = self._filtros_y_orden(request)
        filas = container.exportar_movimientos().ejecutar(
            ExportarMovimientosInputDTO(self.hogar.pk, self.actor, filtros, orden)
        )

        class Eco:
            def write(self, valor):
                return valor

        escritor = csv.writer(Eco(), delimiter=";")
        cabecera = escritor.writerow(["fecha", "concepto", "importe", "cuenta", "categoría", "etiquetas"])
        lineas = (
            escritor.writerow(
                [
                    f.fecha,
                    texto_csv(f.concepto),  # el texto (de terceros) sin fórmulas
                    str(f.importe).replace(".", ","),  # el importe, tal cual: "-12,50" es un número
                    texto_csv(f.cuenta),
                    texto_csv(f.categoria or ""),
                    texto_csv(",".join(f.etiquetas)),
                ]
            )
            for f in filas
        )
        respuesta = StreamingHttpResponse(
            (x for bloque in ([cabecera], lineas) for x in bloque), content_type="text/csv; charset=utf-8"
        )
        respuesta["Content-Disposition"] = f'attachment; filename="movimientos-{self.hogar.pk}.csv"'
        return respuesta
