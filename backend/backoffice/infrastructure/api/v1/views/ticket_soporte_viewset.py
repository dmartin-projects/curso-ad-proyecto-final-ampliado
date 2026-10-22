# backoffice/infrastructure/api/v1/views/ticket_soporte_viewset.py — adapter de entrada HTTP del personal de soporte (módulos 79 y 88)
#
# El backoffice es un adapter de entrada más: lee de TODOS los hogares con sus use cases de consulta y, para
# cambiar algo, llama a los mismos use cases que la API de los usuarios (mismas reglas, eventos y tareas) con un
# Actor.soporte: quedan registrados en la auditoría con el usuario de soporte que los hizo.
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from backoffice.application.listar_tickets_soporte_use_case.dtos.listar_tickets_soporte_input_dto import (
    ListarTicketsSoporteInputDTO,
)
from backoffice.application.localizar_tickets_use_case.dtos.localizar_tickets_input_dto import LocalizarTicketsInputDTO
from backoffice.application.obtener_ticket_soporte_use_case.dtos.obtener_ticket_soporte_input_dto import (
    ObtenerTicketSoporteInputDTO,
)
from backoffice.infrastructure import container
from backoffice.infrastructure.api.permissions.personal import PERSONAL
from backoffice.infrastructure.api.v1.presenters import soporte_presenters as presentar
from backoffice.infrastructure.api.v1.serializers.ids_serializer import IdsSerializer
from backoffice.infrastructure.api.v1.serializers.resultado_lote_serializer import ResultadoLoteSerializer
from backoffice.infrastructure.api.v1.serializers.ticket_soporte_serializer import TicketSoporteSerializer
from backoffice.infrastructure.api.v1.views.listado_soporte_mixin import ListadoSoporteMixin
from core.domain.vo.actor import Actor
from core.infrastructure.api.views import consultas
from tickets.application.reprocesar_ticket_use_case.dtos.reprocesar_ticket_input_dto import ReprocesarTicketInputDTO
from tickets.domain.exceptions.estado_no_permitido_exception import (
    EstadoNoPermitidoException as TicketNoReprocesableException,
)
from tickets.infrastructure import container as tickets
from tickets.models import Ticket as TicketModel


class TicketSoporteViewSet(ListadoSoporteMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketSoporteSerializer
    permission_classes = PERSONAL
    permisos_por_accion = {
        "list": ["tickets.view_ticket"],
        "retrieve": ["tickets.view_ticket"],
        "reprocesar": ["tickets.change_ticket"],
    }
    modelo = TicketModel
    filtros_a_campos = {"hogar": "hogar_id"}
    filterset_fields = ["estado", "hogar"]
    search_fields = ["=id", "hogar__nombre", "subido_por__email"]
    ordering = ["-creado"]

    @extend_schema(
        parameters=[OpenApiParameter("atascado", bool, description="Más de 15 min sin terminar")],
    )
    def list(self, request, *args, **kwargs):
        atascados = request.query_params.get("atascado") == "true"
        entrada = ListarTicketsSoporteInputDTO(self._query(request), solo_atascados=atascados)
        return self._pagina(request, container.listar_tickets_soporte().ejecutar(entrada), presentar.ticket)

    def retrieve(self, request, *args, **kwargs):
        entrada = ObtenerTicketSoporteInputDTO(consultas.id_de_la_url(self))
        leido = self._o_404(container.obtener_ticket_soporte().ejecutar(entrada))
        return Response(self.get_serializer(presentar.ticket(leido)).data)

    @extend_schema(request=IdsSerializer, responses=ResultadoLoteSerializer)
    @action(detail=False, methods=["post"])
    def reprocesar(self, request, *args, **kwargs):
        """Reprocesa varios tickets (los que no estén en error o en revisión se omiten)."""
        ids = IdsSerializer(data=request.data)
        ids.is_valid(raise_exception=True)
        hechos = omitidos = 0
        soporte = Actor.soporte(request.user.pk)
        encontrados = container.localizar_tickets().ejecutar(LocalizarTicketsInputDTO(tuple(ids.validated_data["ids"])))
        for ticket_id, hogar_id in encontrados:
            try:  # el mismo use case que la API: reglas, gasto propuesto descartado, tarea encolada y auditoría
                tickets.reprocesar_ticket().ejecutar(ReprocesarTicketInputDTO(hogar_id, soporte, ticket_id))
                hechos += 1
            except TicketNoReprocesableException:
                omitidos += 1
        return Response({"hechos": hechos, "omitidos": omitidos})
