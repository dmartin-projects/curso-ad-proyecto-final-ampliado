# asistente/application/indexar_ayuda_use_case/i_indexar_ayuda_use_case.py (módulo 100)
from abc import ABC, abstractmethod

from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_input_dto import IndexarAyudaInputDTO
from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_output_dto import IndexarAyudaOutputDTO


class IIndexarAyudaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: IndexarAyudaInputDTO) -> IndexarAyudaOutputDTO:
        """Pone el índice al día con los .md de la ayuda: lo nuevo y lo cambiado, se calcula; lo que ya no está, fuera."""
