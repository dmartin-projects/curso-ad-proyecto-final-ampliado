# notificaciones/infrastructure/database/repositories/notificacion_query_service_orm.py — INotificacionQueryService con el ORM (módulo 88)
from core.infrastructure.database import paginacion
from notificaciones.domain.read_models.notificacion_listada import NotificacionListada
from notificaciones.domain.repositories.i_notificacion_query_service import INotificacionQueryService
from notificaciones.domain.repositories.queries.notificaciones_query import NotificacionesQuery
from notificaciones.infrastructure.database.models.notificacion_model import Notificacion as NotificacionModel

ORDEN = ("-creado", "-id")


def _a_read_model(n: NotificacionModel) -> NotificacionListada:
    return NotificacionListada(
        id=n.pk,
        tipo=n.tipo,
        titulo=n.titulo,
        mensaje=n.mensaje,
        enlace=n.enlace,
        hogar_id=n.hogar_id,
        datos=n.datos,
        leida=n.leida,
        creado=n.creado,
    )


class NotificacionQueryServiceORM(INotificacionQueryService):
    def listar(self, query: NotificacionesQuery):
        qs = NotificacionModel.objects.filter(usuario_id=query.usuario_id)
        if query.leida is not None:
            qs = qs.filter(leida=query.leida)
        if query.tipo is not None:
            qs = qs.filter(tipo=query.tipo)
        if query.hogar_id is not None:
            qs = qs.filter(hogar_id=query.hogar_id)
        return paginacion.por_cursor(qs, query.paginacion, ORDEN, _a_read_model)

    def detalle(self, usuario_id, notificacion_id):
        fila = NotificacionModel.objects.filter(usuario_id=usuario_id, pk=notificacion_id).first()
        return None if fila is None else _a_read_model(fila)

    def contar_no_leidas(self, usuario_id) -> int:
        return NotificacionModel.objects.filter(usuario_id=usuario_id, leida=False).count()
