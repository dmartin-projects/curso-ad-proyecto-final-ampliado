# asistente/application/ports/i_programador_de_analisis.py — el análisis del mes, en segundo plano (módulo 105)
from abc import ABC, abstractmethod


class IProgramadorDeAnalisis(ABC):
    @abstractmethod
    def programar(self, usuario_id: int, hogar_id: int, mes: str, tarea: str) -> None:
        """Encola el análisis (tras el commit). `tarea`: el id con el que llegan sus avisos de progreso."""
