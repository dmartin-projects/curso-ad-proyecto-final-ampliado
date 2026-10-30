# asistente/application/crear_carpeta_use_case/i_crear_carpeta_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.crear_carpeta_use_case.dtos.crear_carpeta_input_dto import CrearCarpetaInputDTO
from asistente.application.shared.dtos.carpeta_output_dto import CarpetaOutputDTO


class ICrearCarpetaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CrearCarpetaInputDTO) -> CarpetaOutputDTO:
        """Una carpeta de quien pide, en ese hogar. El nombre no se repite."""
