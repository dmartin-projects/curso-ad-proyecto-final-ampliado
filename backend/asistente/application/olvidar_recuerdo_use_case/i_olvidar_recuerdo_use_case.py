# asistente/application/olvidar_recuerdo_use_case/i_olvidar_recuerdo_use_case.py (módulo 99)
from abc import ABC, abstractmethod

from asistente.application.olvidar_recuerdo_use_case.dtos.olvidar_recuerdo_input_dto import OlvidarRecuerdoInputDTO


class IOlvidarRecuerdoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: OlvidarRecuerdoInputDTO) -> None:
        """Borra uno de los recuerdos de quien pide (de otro, RecuerdoNoEncontradoException)."""
