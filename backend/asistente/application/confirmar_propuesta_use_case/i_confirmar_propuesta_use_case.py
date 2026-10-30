# asistente/application/confirmar_propuesta_use_case/i_confirmar_propuesta_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.confirmar_propuesta_use_case.dtos.confirmar_propuesta_input_dto import (
    ConfirmarPropuestaInputDTO,
)
from asistente.application.shared.dtos.propuesta_output_dto import PropuestaOutputDTO


class IConfirmarPropuestaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ConfirmarPropuestaInputDTO) -> PropuestaOutputDTO:
        """Ejecuta lo propuesto con el use case de comando de la app dueña y el Actor de quien confirma."""
