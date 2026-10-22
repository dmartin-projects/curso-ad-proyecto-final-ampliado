# tickets/infrastructure/database/repositories/ticket_query_service_orm.py — ITicketQueryService con el ORM (módulo 88)
from functools import reduce
from operator import and_

from django.db.models import Q
from django.utils import timezone

from core.infrastructure.database import paginacion
from tickets.domain.enums.estado_ticket import ATASCADO, SIN_TERMINAR
from tickets.domain.read_models.ticket_listado import GastoDelTicket, LineaListada, TicketListado
from tickets.domain.repositories.i_ticket_query_service import ITicketQueryService
from tickets.domain.repositories.queries.tickets_query import TicketsQuery
from tickets.infrastructure.database.models.ticket_model import Ticket as TicketModel

CAMPOS_BUSQUEDA = ("nombre_original", "texto_ocr")


def _a_read_model(t: TicketModel) -> TicketListado:
    m = t.movimiento
    return TicketListado(
        id=t.pk,
        estado=t.estado,
        cuenta_id=t.cuenta_id,
        nombre_original=t.nombre_original,
        tipo=t.tipo,
        archivo=t.archivo.name,
        confianza=t.confianza,
        error=t.error,
        datos_ia=t.datos_ia,
        intentos=t.intentos,
        lineas=tuple(
            LineaListada(li.orden, li.descripcion, li.cantidad, li.precio_unitario, li.importe) for li in t.lineas.all()
        ),
        gasto=None if m is None else GastoDelTicket(m.pk, m.fecha, m.importe, m.concepto, m.categoria_id, m.revisado),
        creado=t.creado,
        procesado_en=t.procesado_en,
    )


def atascados():
    """Pendientes o procesando sin moverse desde hace 15 minutos (soporte, módulo 79; métrica, módulo 84)."""
    return TicketModel.objects.filter(estado__in=SIN_TERMINAR, actualizado__lt=timezone.now() - ATASCADO)


class TicketQueryServiceORM(ITicketQueryService):
    @staticmethod
    def _del_hogar(hogar_id: int):
        return TicketModel.objects.filter(hogar_id=hogar_id).select_related("movimiento").prefetch_related("lineas")

    def listar(self, query: TicketsQuery):
        qs = self._del_hogar(query.hogar_id)
        if query.estado is not None:
            qs = qs.filter(estado=query.estado)
        if query.cuenta_id is not None:
            qs = qs.filter(cuenta_id=query.cuenta_id)
        if query.busqueda:  # cada término en alguno de los campos; todos los términos a la vez (SearchFilter)
            terminos = (
                reduce(Q.__or__, (Q(**{f"{c}__icontains": t}) for c in CAMPOS_BUSQUEDA)) for t in query.busqueda
            )
            qs = qs.filter(reduce(and_, terminos))
        return paginacion.por_numero(qs.order_by(*(query.orden or ("-creado",))), query.paginacion, _a_read_model)

    def detalle(self, hogar_id, ticket_id):
        fila = self._del_hogar(hogar_id).filter(pk=ticket_id).first()
        return None if fila is None else _a_read_model(fila)

    def contar_atascados(self) -> int:
        return atascados().count()
