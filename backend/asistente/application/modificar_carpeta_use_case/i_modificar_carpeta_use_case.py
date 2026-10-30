# asistente/application/modificar_carpeta_use_case/i_modificar_carpeta_use_case.py (módulo 97, ejercicio 1)
from abc import ABC, abstractmethod

from asistente.application.modificar_carpeta_use_case.dtos.modificar_carpeta_input_dto import ModificarCarpetaInputDTO
from asistente.application.shared.dtos.carpeta_output_dto import CarpetaOutputDTO


class IModificarCarpetaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ModificarCarpetaInputDTO) -> CarpetaOutputDTO:
        """Cambiar el nombre de una carpeta de quien pide (sin repetir el de otra suya)."""
