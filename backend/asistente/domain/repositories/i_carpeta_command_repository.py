# asistente/domain/repositories/i_carpeta_command_repository.py — escribir carpetas (módulo 97)
from abc import ABC, abstractmethod

from asistente.domain.bo.carpeta import Carpeta


class ICarpetaCommandRepository(ABC):
    @abstractmethod
    def obtener(self, usuario_id: int, hogar_id: int, carpeta_id: int) -> Carpeta:
        """La de esa persona en ese hogar, o CarpetaNoEncontradaException."""

    @abstractmethod
    def guardar(self, carpeta: Carpeta) -> None:
        """Crea o actualiza. Un nombre repetido (de esa persona en ese hogar): CarpetaRepetidaException."""

    @abstractmethod
    def eliminar(self, carpeta: Carpeta) -> None:
        """Sus conversaciones NO se borran: se quedan fuera de toda carpeta."""
