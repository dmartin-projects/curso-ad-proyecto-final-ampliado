# finanzas/application/descartar_propuestos_use_case/i_descartar_propuestos_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from finanzas.application.descartar_propuestos_use_case.dtos.descartar_propuestos_input_dto import (
    DescartarPropuestosInputDTO,
)


class IDescartarPropuestosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: DescartarPropuestosInputDTO) -> list[int]: ...
