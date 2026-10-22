# hogares/infrastructure/database/repositories/miembro_query_service_orm.py — IMiembroQueryService con el ORM (módulo 88)
from hogares.domain.read_models.miembro_listado import MiembroListado
from hogares.domain.repositories.i_miembro_query_service import IMiembroQueryService
from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel


def _a_read_model(m: MembresiaModel) -> MiembroListado:
    return MiembroListado(
        id=m.pk,
        usuario_id=m.usuario_id,
        email=m.usuario.email,
        nombre=m.usuario.get_full_name(),
        rol=m.rol,
        creado=m.creado,
    )


class MiembroQueryServiceORM(IMiembroQueryService):
    @staticmethod
    def _del_hogar(hogar_id: int):
        return MembresiaModel.objects.filter(hogar_id=hogar_id).select_related("usuario")

    def listar(self, query):
        return [_a_read_model(m) for m in self._del_hogar(query.hogar_id).order_by(*(query.orden or ("creado",)))]

    def detalle(self, hogar_id, membresia_id):
        fila = self._del_hogar(hogar_id).filter(pk=membresia_id).first()
        return None if fila is None else _a_read_model(fila)
