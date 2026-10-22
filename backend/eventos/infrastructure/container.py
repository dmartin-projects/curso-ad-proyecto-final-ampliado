# eventos/infrastructure/container.py — composition root del outbox (módulo 88)
#
# Las demás apps piden aquí su outbox (finanzas y hogares lo dan a sus publicadores): es una dependencia más, y en un
# test se puede cambiar.
from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from eventos.application.ports.i_outbox import IOutbox
from eventos.application.publicar_pendientes_use_case.i_publicar_pendientes_use_case import (
    IPublicarPendientesUseCase,
)
from eventos.application.publicar_pendientes_use_case.publicar_pendientes_use_case import PublicarPendientesUseCase
from eventos.infrastructure.database.repositories.evento_pendiente_command_repository_orm import (
    EventoPendienteCommandRepositoryORM,
)
from eventos.infrastructure.messaging.broker_kafka import BrokerKafka
from eventos.infrastructure.messaging.outbox_django import OutboxDjango


def outbox() -> IOutbox:
    return OutboxDjango()


def publicar_pendientes(productor, *, timeout: float = 30) -> IPublicarPendientesUseCase:
    return PublicarPendientesUseCase(
        pendientes=EventoPendienteCommandRepositoryORM(),
        broker=BrokerKafka(productor, timeout=timeout),
        uow=UnidadDeTrabajoDjango(),
        reloj=RelojDjango(),
    )
