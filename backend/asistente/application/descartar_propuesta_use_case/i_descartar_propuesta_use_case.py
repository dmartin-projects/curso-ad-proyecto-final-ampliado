# asistente/application/descartar_propuesta_use_case/i_descartar_propuesta_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.descartar_propuesta_use_case.dtos.descartar_propuesta_input_dto import (
    DescartarPropuestaInputDTO,
)
from asistente.application.shared.dtos.propuesta_output_dto import PropuestaOutputDTO


class IDescartarPropuestaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: DescartarPropuestaInputDTO) -> PropuestaOutputDTO:
        """La propuesta queda descartada y ya no se puede confirmar."""
