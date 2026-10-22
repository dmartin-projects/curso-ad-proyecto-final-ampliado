# notificaciones/infrastructure/database/repositories/notificacion_command_repository_orm.py — INotificacionCommandRepository con el ORM (módulo 88)
from notificaciones.domain.repositories.i_notificacion_command_repository import INotificacionCommandRepository
from notificaciones.infrastructure.database.models.notificacion_model import Notificacion as NotificacionModel


class NotificacionCommandRepositoryORM(INotificacionCommandRepository):
    def crear_varias(self, notificaciones) -> None:
        filas = NotificacionModel.objects.bulk_create(
            NotificacionModel(
                usuario_id=n.usuario_id,
                hogar_id=n.hogar_id,
                tipo=n.tipo,
                titulo=n.titulo,
                mensaje=n.mensaje,
                enlace=n.enlace,
                datos=n.datos,
            )  # fmt: skip
            for n in notificaciones
        )
        for n, fila in zip(notificaciones, filas, strict=True):
            n.id = fila.pk
