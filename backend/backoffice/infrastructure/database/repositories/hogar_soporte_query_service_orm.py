# backoffice/infrastructure/database/repositories/hogar_soporte_query_service_orm.py — IHogarSoporteQueryService con el ORM (módulo 88)
from backoffice.domain.read_models.hogar_soporte import HogarSoporte
from backoffice.domain.read_models.miembro_soporte import MiembroSoporte
from backoffice.domain.repositories.i_hogar_soporte_query_service import IHogarSoporteQueryService
from backoffice.infrastructure.database.repositories.listados import listar
from core.infrastructure.database.consultas import contar
from finanzas.models import Movimiento as MovimientoModel
from hogares.models import Hogar as HogarModel
from hogares.models import Membresia as MembresiaModel

BUSQUEDA = ("nombre", "=id", "membresias__usuario__email")


def _con_contadores(*, buscando: bool = False):
    qs = HogarModel.objects.annotate(
        num_miembros=contar(MembresiaModel, "hogar"), num_movimientos=contar(MovimientoModel, "hogar")
    )
    return qs.distinct() if buscando else qs  # el JOIN de la búsqueda duplica


def _a_read_model(h: HogarModel, miembros=()) -> HogarSoporte:
    return HogarSoporte(h.pk, h.nombre, h.zona_horaria, h.num_miembros, h.num_movimientos, h.creado, tuple(miembros))


class HogarSoporteQueryServiceORM(IHogarSoporteQueryService):
    def listar(self, query):
        return listar(_con_contadores(buscando=bool(query.busqueda)), query, BUSQUEDA, _a_read_model)

    def detalle(self, hogar_id):
        fila = _con_contadores().prefetch_related("membresias__usuario").filter(pk=hogar_id).first()
        if fila is None:
            return None
        miembros = (MiembroSoporte(m.usuario_id, m.usuario.email, m.rol) for m in fila.membresias.all())
        return _a_read_model(fila, miembros)
