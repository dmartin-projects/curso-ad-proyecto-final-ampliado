# backoffice/application/obtener_tarea_programada_use_case/i_obtener_tarea_programada_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.obtener_tarea_programada_use_case.dtos.obtener_tarea_programada_input_dto import (
    ObtenerTareaProgramadaInputDTO,
)
from backoffice.application.shared.dtos.tarea_programada_soporte_output_dto import TareaProgramadaSoporteOutputDTO


class IObtenerTareaProgramadaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerTareaProgramadaInputDTO) -> TareaProgramadaSoporteOutputDTO | None: ...
