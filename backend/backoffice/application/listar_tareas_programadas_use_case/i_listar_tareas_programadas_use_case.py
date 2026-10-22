# backoffice/application/listar_tareas_programadas_use_case/i_listar_tareas_programadas_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.listar_tareas_programadas_use_case.dtos.listar_tareas_programadas_input_dto import (
    ListarTareasProgramadasInputDTO,
)
from backoffice.application.shared.dtos.tarea_programada_soporte_output_dto import TareaProgramadaSoporteOutputDTO


class IListarTareasProgramadasUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarTareasProgramadasInputDTO) -> list[TareaProgramadaSoporteOutputDTO]: ...
