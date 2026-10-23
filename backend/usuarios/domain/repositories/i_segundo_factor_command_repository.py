# usuarios/domain/repositories/i_segundo_factor_command_repository.py — el segundo factor de cada cuenta (módulo 92)
from abc import ABC, abstractmethod

from usuarios.domain.bo.segundo_factor import SegundoFactor


class ISegundoFactorCommandRepository(ABC):
    @abstractmethod
    def de(self, usuario_id: int, *, bloquear: bool = False) -> SegundoFactor:
        """El de esa cuenta (uno vacío si nunca lo ha configurado). Con `bloquear`, nadie más lo cambia hasta el final
        de la transacción: dos intentos a la vez con el mismo código no lo aceptan los dos."""

    @abstractmethod
    def guardar(self, segundo: SegundoFactor) -> None:
        """Cifra el secreto antes de guardarlo."""
        ...
