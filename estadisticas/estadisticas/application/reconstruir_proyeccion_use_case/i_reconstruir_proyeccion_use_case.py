# estadisticas/application/reconstruir_proyeccion_use_case/i_reconstruir_proyeccion_use_case.py (módulo 89)
from abc import ABC, abstractmethod


class IReconstruirProyeccionUseCase(ABC):
    @abstractmethod
    def ejecutar(self) -> None: ...
