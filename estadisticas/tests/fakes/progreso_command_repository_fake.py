"""IProgresoCommandRepository en memoria (módulo 89)."""

from datetime import datetime

from estadisticas.domain.repositories.i_progreso_command_repository import IProgresoCommandRepository
from tests.fakes.memoria import Memoria


class ProgresoCommandRepositoryFake(IProgresoCommandRepository):
    def __init__(self, memoria: Memoria):
        self.memoria = memoria

    def guardar(self, topic: str, particion: int, offset: int, marca: datetime) -> None:
        self.memoria.progreso[(topic, particion)] = (offset, marca)

    def vaciar(self) -> None:
        self.memoria.progreso.clear()
