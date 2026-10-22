# backoffice/infrastructure/database/repositories/usuario_soporte_query_service_orm.py — IUsuarioSoporteQueryService con el ORM (módulo 88)
from django.contrib.auth import get_user_model

from backoffice.domain.read_models.usuario_soporte import UsuarioSoporte
from backoffice.domain.repositories.i_usuario_soporte_query_service import IUsuarioSoporteQueryService
from backoffice.infrastructure.database.repositories.listados import listar

BUSQUEDA = ("email", "nombre", "apellidos")


def _a_read_model(u) -> UsuarioSoporte:
    return UsuarioSoporte(u.pk, u.email, u.nombre, u.apellidos, u.is_active, u.is_staff, u.fecha_alta, u.last_login)


class UsuarioSoporteQueryServiceORM(IUsuarioSoporteQueryService):
    def listar(self, query):
        return listar(get_user_model().objects.order_by("-fecha_alta"), query, BUSQUEDA, _a_read_model)

    def detalle(self, usuario_id):
        fila = get_user_model().objects.filter(pk=usuario_id).first()
        return None if fila is None else _a_read_model(fila)
