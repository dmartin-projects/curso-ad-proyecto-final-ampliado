# asistente/application/ports/i_membresias.py — de qué hogares es miembro quien pregunta (módulos 94 y 97)
from abc import ABC, abstractmethod

from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario
from asistente.domain.read_models.miembro_del_hogar import MiembroDelHogar
from core.domain.vo.actor import Actor


class IMembresias(ABC):
    """hogares, vista desde el asistente (anti-corruption layer: infrastructure/hogares/)."""

    @abstractmethod
    def hogar_de(self, usuario_id: int, hogar_id: int) -> HogarDelUsuario | None:
        """El hogar con el rol de esa persona, o None si no es miembro (para ella no existe)."""

    @abstractmethod
    def hogares_de(self, usuario_id: int) -> tuple[HogarDelUsuario, ...]:
        """Módulo 104: todos sus hogares, con su rol en cada uno (listar_hogares del servidor MCP)."""

    @abstractmethod
    def miembros(self, actor: Actor, hogar_id: int) -> tuple[MiembroDelHogar, ...]:
        """Quién forma parte del hogar, con el use case de consulta de hogares (módulo 97)."""
