# asistente/application/ports/i_membresias.py — de qué hogares es miembro quien pregunta (módulo 94)
from abc import ABC, abstractmethod

from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario


class IMembresias(ABC):
    """hogares, vista desde el asistente (anti-corruption layer: infrastructure/hogares/)."""

    @abstractmethod
    def hogar_de(self, usuario_id: int, hogar_id: int) -> HogarDelUsuario | None:
        """El hogar con el rol de esa persona, o None si no es miembro (para ella no existe)."""
