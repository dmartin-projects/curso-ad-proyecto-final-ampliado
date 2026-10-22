# backoffice/application/obtener_movimiento_soporte_use_case/i_obtener_movimiento_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.obtener_movimiento_soporte_use_case.dtos.obtener_movimiento_soporte_input_dto import (
    ObtenerMovimientoSoporteInputDTO,
)
from backoffice.application.shared.dtos.movimiento_soporte_output_dto import MovimientoSoporteOutputDTO


class IObtenerMovimientoSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerMovimientoSoporteInputDTO) -> MovimientoSoporteOutputDTO | None: ...
