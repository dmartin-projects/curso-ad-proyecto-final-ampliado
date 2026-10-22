# backoffice/infrastructure/api/v1/views/movimiento_soporte_viewset.py — adapter de entrada HTTP del personal de soporte (módulos 79 y 88)
#
# El backoffice es un adapter de entrada más: lee de TODOS los hogares con sus use cases de consulta y, para
# cambiar algo, llama a los mismos use cases que la API de los usuarios (mismas reglas, eventos y tareas) con un
# Actor.soporte: quedan registrados en la auditoría con el usuario de soporte que los hizo.
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from backoffice.application.listar_movimientos_soporte_use_case.dtos.listar_movimientos_soporte_input_dto import (
    ListarMovimientosSoporteInputDTO,
)
from backoffice.application.obtener_hogar_de_categoria_use_case.dtos.obtener_hogar_de_categoria_input_dto import (
    ObtenerHogarDeCategoriaInputDTO,
)
from backoffice.application.obtener_movimiento_soporte_use_case.dtos.obtener_movimiento_soporte_input_dto import (
    ObtenerMovimientoSoporteInputDTO,
)
from backoffice.infrastructure import container
from backoffice.infrastructure.api.permissions.personal import PERSONAL
from backoffice.infrastructure.api.v1.presenters import soporte_presenters as presentar
from backoffice.infrastructure.api.v1.serializers.movimiento_soporte_serializer import MovimientoSoporteSerializer
from backoffice.infrastructure.api.v1.serializers.recategorizar_soporte_serializer import (
    RecategorizarSoporteSerializer,
)
from backoffice.infrastructure.api.v1.serializers.resultado_lote_serializer import ResultadoLoteSerializer
from backoffice.infrastructure.api.v1.views.listado_soporte_mixin import ListadoSoporteMixin
from core.domain.vo.actor import Actor
from core.infrastructure.api.views import consultas
from finanzas.application.recategorizar_movimientos_use_case.dtos.recategorizar_movimientos_input_dto import (
    RecategorizarMovimientosInputDTO,
)
from finanzas.infrastructure import container as finanzas
from finanzas.models import Movimiento as MovimientoModel


class MovimientoSoporteViewSet(ListadoSoporteMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = MovimientoSoporteSerializer
    permission_classes = PERSONAL
    permisos_por_accion = {
        "list": ["finanzas.view_movimiento"],
        "retrieve": ["finanzas.view_movimiento"],
        "recategorizar": ["finanzas.change_movimiento"],
    }
    modelo = MovimientoModel
    filtros_a_campos = {"hogar": "hogar_id", "categoria": "categoria_id"}
    filterset_fields = ["hogar", "revisado", "origen", "categoria"]
    search_fields = ["concepto", "comercio__nombre"]
    ordering = ["-fecha", "-id"]

    def list(self, request, *args, **kwargs):
        entrada = ListarMovimientosSoporteInputDTO(self._query(request))
        return self._pagina(request, container.listar_movimientos_soporte().ejecutar(entrada), presentar.movimiento)

    def retrieve(self, request, *args, **kwargs):
        entrada = ObtenerMovimientoSoporteInputDTO(consultas.id_de_la_url(self))
        leido = self._o_404(container.obtener_movimiento_soporte().ejecutar(entrada))
        return Response(self.get_serializer(presentar.movimiento(leido)).data)

    @extend_schema(request=RecategorizarSoporteSerializer, responses=ResultadoLoteSerializer)
    @action(detail=False, methods=["post"])
    def recategorizar(self, request, *args, **kwargs):
        datos = RecategorizarSoporteSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        categoria = datos.validated_data["categoria"]
        hogar_id = container.obtener_hogar_de_categoria().ejecutar(ObtenerHogarDeCategoriaInputDTO(categoria))
        if hogar_id is None:
            raise ValidationError({"categoria": ["No existe."]})
        ids = datos.validated_data["ids"]
        # El mismo use case que la API: solo los movimientos de ESE hogar, revisados, con su outbox, sus avisos y su
        # auditoría (a nombre del personal de soporte)
        entrada = RecategorizarMovimientosInputDTO(hogar_id, Actor.soporte(request.user.pk), tuple(ids), categoria)
        n = finanzas.recategorizar_movimientos().ejecutar(entrada)
        return Response({"hechos": n, "omitidos": len(set(ids)) - n})
