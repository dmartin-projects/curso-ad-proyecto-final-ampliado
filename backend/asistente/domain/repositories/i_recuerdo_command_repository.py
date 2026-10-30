# asistente/domain/repositories/i_recuerdo_command_repository.py (módulo 99)
from abc import ABC, abstractmethod

from asistente.domain.bo.recuerdo import Recuerdo


class IRecuerdoCommandRepository(ABC):
    @abstractmethod
    def obtener(self, usuario_id: int, hogar_id: int, recuerdo_id: int) -> Recuerdo:
        """El de esa persona en ese hogar, o RecuerdoNoEncontradoException."""

    @abstractmethod
    def guardar(self, recuerdo: Recuerdo) -> None: ...

    @abstractmethod
    def eliminar(self, recuerdo: Recuerdo) -> None: ...

    @abstractmethod
    def contar(self, usuario_id: int, hogar_id: int) -> int: ...
