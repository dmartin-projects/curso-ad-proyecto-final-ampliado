# hogares/infrastructure/database/repositories/hogar_query_service_orm.py — IHogarQueryService con el ORM (módulo 88)
from django.db.models import Count, OuterRef, Subquery

from core.infrastructure.database import paginacion
from hogares.domain.read_models.hogar_listado import HogarListado
from hogares.domain.repositories.i_hogar_query_service import IHogarQueryService
from hogares.domain.repositories.queries.hogares_query import HogaresQuery
from hogares.infrastructure.database.models.hogar_model import Hogar as HogarModel
from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel


def _a_read_model(h: HogarModel) -> HogarListado:
    return HogarListado(
        id=h.pk,
        nombre=h.nombre,
        moneda=h.moneda,
        zona_horaria=h.zona_horaria,
        mi_rol=h.mi_rol,
        num_miembros=h.num_miembros,
        creado=h.creado,
    )


class HogarQueryServiceORM(IHogarQueryService):
    @staticmethod
    def _mis_hogares(usuario_id: int):
        """Los hogares del usuario con su rol en cada uno y cuántos miembros tiene (una consulta)."""
        mi_rol = MembresiaModel.objects.filter(hogar=OuterRef("pk"), usuario_id=usuario_id).values("rol")[:1]
        return HogarModel.objects.filter(membresias__usuario_id=usuario_id).annotate(
            mi_rol=Subquery(mi_rol), num_miembros=Count("membresias", distinct=True)
        )

    def listar(self, query: HogaresQuery):
        qs = self._mis_hogares(query.usuario_id).order_by(*(query.orden or ("nombre",)))
        return paginacion.por_numero(qs, query.paginacion, _a_read_model)

    def detalle(self, usuario_id, hogar_id):
        fila = self._mis_hogares(usuario_id).filter(pk=hogar_id).first()
        return None if fila is None else _a_read_model(fila)
