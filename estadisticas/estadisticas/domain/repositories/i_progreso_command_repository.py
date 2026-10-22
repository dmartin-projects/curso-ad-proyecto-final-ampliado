# estadisticas/domain/repositories/i_progreso_command_repository.py — el lado de ESCRITURA (CQRS, módulo 89)
from abc import ABC, abstractmethod
from datetime import datetime


class IProgresoCommandRepository(ABC):
    """Hasta dónde ha llegado la proyección en cada partición (para decir "datos de hace X segundos")."""

    @abstractmethod
    def guardar(self, topic: str, particion: int, offset: int, marca: datetime) -> None: ...

    @abstractmethod
    def vaciar(self) -> None: ...
