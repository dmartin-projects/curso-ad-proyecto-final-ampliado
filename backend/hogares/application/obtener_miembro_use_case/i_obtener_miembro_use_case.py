# hogares/application/obtener_miembro_use_case/i_obtener_miembro_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.application.obtener_miembro_use_case.dtos.obtener_miembro_input_dto import ObtenerMiembroInputDTO
from hogares.application.shared.dtos.miembro_listado_output_dto import MiembroListadoOutputDTO


class IObtenerMiembroUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerMiembroInputDTO) -> MiembroListadoOutputDTO | None: ...
