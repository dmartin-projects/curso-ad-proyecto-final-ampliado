# importaciones/application/subir_extracto_use_case/i_subir_extracto_use_case.py (módulos 75 y 88)
from abc import ABC, abstractmethod

from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO
from importaciones.application.subir_extracto_use_case.dtos.subir_extracto_input_dto import SubirExtractoInputDTO


class ISubirExtractoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: SubirExtractoInputDTO) -> ImportacionOutputDTO: ...
