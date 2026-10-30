# asistente/application/ports/i_control_de_analisis.py — uno a la vez, y pararlo (ejercicios 1 y 3 del 105)
from abc import ABC, abstractmethod


class IControlDeAnalisis(ABC):
    """El estado de los análisis en marcha, compartido entre la API y los workers (ControlDeAnalisisEnCache: Redis)."""

    @abstractmethod
    def empezar(self, usuario_id: int, hogar_id: int, tarea: str) -> bool:
        """False si esa persona ya tiene uno en marcha en ese hogar (ejercicio 3). Caduca solo: un worker que muere no
        deja el análisis bloqueado para siempre."""

    @abstractmethod
    def terminar(self, usuario_id: int, hogar_id: int) -> None: ...

    @abstractmethod
    def cancelar(self, usuario_id: int, tarea: str) -> None:
        """Ejercicio 1: la marca que el análisis mira entre especialista y especialista. Solo las de esa persona."""

    @abstractmethod
    def cancelado(self, usuario_id: int, tarea: str) -> bool: ...
