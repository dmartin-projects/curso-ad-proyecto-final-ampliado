# asistente/domain/repositories/i_propuesta_command_repository.py — escribir propuestas (módulo 97)
from abc import ABC, abstractmethod

from asistente.domain.bo.propuesta import Propuesta


class IPropuestaCommandRepository(ABC):
    @abstractmethod
    def obtener(self, usuario_id: int, hogar_id: int, propuesta_id: int, bloquear: bool = False) -> Propuesta:
        """La de esa persona en ese hogar, o PropuestaNoEncontradaException. Con `bloquear`, nadie más la toca hasta
        el final de la transacción (SELECT … FOR UPDATE): dos "Confirmar" a la vez no la ejecutan dos veces."""

    @abstractmethod
    def guardar(self, propuesta: Propuesta) -> None: ...
