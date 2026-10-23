# usuarios/application/regenerar_codigos_use_case/i_regenerar_codigos_use_case.py (módulo 92, ejercicio 2)
from abc import ABC, abstractmethod

from usuarios.application.regenerar_codigos_use_case.dtos.regenerar_codigos_input_dto import RegenerarCodigosInputDTO


class IRegenerarCodigosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: RegenerarCodigosInputDTO) -> list[str]: ...
