# backoffice/infrastructure/database/repositories/ticket_soporte_query_service_orm.py — ITicketSoporteQueryService con el ORM (módulo 88)
from backoffice.domain.read_models.ticket_soporte import TicketSoporte
from backoffice.domain.repositories.i_ticket_soporte_query_service import ITicketSoporteQueryService
from backoffice.infrastructure.database.repositories.listados import listar
from tickets.infrastructure.database.repositories.ticket_query_service_orm import atascados
from tickets.models import Ticket as TicketModel

BUSQUEDA = ("=id", "hogar__nombre", "subido_por__email")


def _a_read_model(t: TicketModel) -> TicketSoporte:
    return TicketSoporte(
        id=t.pk,
        hogar_id=t.hogar_id,
        hogar_nombre=t.hogar.nombre,
        subido_por_email=None if t.subido_por is None else t.subido_por.email,
        estado=t.estado,
        intentos=t.intentos,
        confianza=t.confianza,
        error=t.error,
        nombre_original=t.nombre_original,
        creado=t.creado,
        actualizado=t.actualizado,
    )


class TicketSoporteQueryServiceORM(ITicketSoporteQueryService):
    @staticmethod
    def _todos():
        return TicketModel.objects.select_related("hogar", "subido_por")

    def listar(self, query, *, solo_atascados=False):
        qs = self._todos()
        if solo_atascados:
            qs = qs.filter(pk__in=atascados().values("pk"))
        return listar(qs, query, BUSQUEDA, _a_read_model)

    def detalle(self, ticket_id):
        fila = self._todos().filter(pk=ticket_id).first()
        return None if fila is None else _a_read_model(fila)

    def localizar(self, ids):
        return list(TicketModel.objects.filter(pk__in=ids).values_list("pk", "hogar_id"))
