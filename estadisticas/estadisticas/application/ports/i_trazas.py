# estadisticas/application/ports/i_trazas.py — un span por mensaje (módulos 84, 85 y 89)
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager

from estadisticas.application.ports.i_traza import ITraza
from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO


class ITrazas(ABC):
    """Un span por mensaje, hijo del que lo publicó (módulo 84): la traza cruza de Django a este servicio."""

    @abstractmethod
    def procesando(self, mensaje: MensajeInputDTO) -> AbstractContextManager[ITraza]: ...
