# backoffice/application/obtener_hogar_de_categoria_use_case/i_obtener_hogar_de_categoria_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.obtener_hogar_de_categoria_use_case.dtos.obtener_hogar_de_categoria_input_dto import (
    ObtenerHogarDeCategoriaInputDTO,
)


class IObtenerHogarDeCategoriaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerHogarDeCategoriaInputDTO) -> int | None: ...
