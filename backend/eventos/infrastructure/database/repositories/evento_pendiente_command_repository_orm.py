# eventos/infrastructure/database/repositories/evento_pendiente_command_repository_orm.py — la bandeja del relay con el ORM (módulos 85 y 88)
from eventos.domain.bo.evento_pendiente import EventoPendiente
from eventos.domain.repositories.i_evento_pendiente_command_repository import IEventoPendienteCommandRepository
from eventos.domain.vo.mensaje import Mensaje
from eventos.infrastructure.database.models.evento_pendiente_model import EventoPendiente as EventoPendienteModel


class EventoPendienteCommandRepositoryORM(IEventoPendienteCommandRepository):
    def pendientes(self, tamano: int) -> list[EventoPendiente]:
        # SKIP LOCKED: si por error arrancan dos relays, no se esperan el uno al otro… pero ver el módulo 85:
        # con dos relays el orden entre lotes ya no está garantizado. Uno solo.
        filas = (
            EventoPendienteModel.objects.select_for_update(skip_locked=True)
            .filter(publicado__isnull=True)
            .order_by("id")[:tamano]
        )
        return [
            EventoPendiente(f.pk, Mensaje(f.topic, f.clave, f.tipo, f.valor), f.traceparent, f.creado) for f in filas
        ]

    def marcar_publicados(self, ids: list[int], cuando) -> None:
        EventoPendienteModel.objects.filter(pk__in=ids).update(publicado=cuando)
