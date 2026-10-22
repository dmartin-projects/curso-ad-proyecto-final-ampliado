"""El relay montado con fakes (módulos 85 y 88): una bandeja y un broker en memoria, sin PostgreSQL y sin Kafka.

El contract test de la bandeja está en tests/infrastructure/database/repositories/test_command_repositories.py.
"""

from datetime import UTC, datetime, timedelta

from core.tests.fakes.reloj_fake import RelojFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from eventos.application.publicar_pendientes_use_case.publicar_pendientes_use_case import PublicarPendientesUseCase
from eventos.tests.fakes.broker_fake import BrokerFake
from eventos.tests.fakes.evento_pendiente_command_repository_fake import EventoPendienteCommandRepositoryFake

AHORA = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)


class Mundo:
    def __init__(self, *mensajes, falla=False):
        self.pendientes = EventoPendienteCommandRepositoryFake(*mensajes, creado=AHORA - timedelta(seconds=2))
        self.broker = BrokerFake(falla)
        self.uow = UnidadDeTrabajoFake(self.pendientes)
        self.publicar = PublicarPendientesUseCase(
            pendientes=self.pendientes, broker=self.broker, uow=self.uow, reloj=RelojFake(AHORA.date(), AHORA)
        )
