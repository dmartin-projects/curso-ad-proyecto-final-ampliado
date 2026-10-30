# asistente/application/eliminar_carpeta_use_case/i_eliminar_carpeta_use_case.py (módulo 97)
from abc import ABC, abstractmethod

from asistente.application.eliminar_carpeta_use_case.dtos.eliminar_carpeta_input_dto import EliminarCarpetaInputDTO


class IEliminarCarpetaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EliminarCarpetaInputDTO) -> None:
        """Sus conversaciones no se borran: se quedan fuera de toda carpeta."""
