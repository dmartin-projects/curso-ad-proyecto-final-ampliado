# finanzas/application/obtener_totales_movimientos_use_case/i_obtener_totales_movimientos_use_case.py (módulo 95)
from abc import ABC, abstractmethod

from finanzas.application.obtener_totales_movimientos_use_case.dtos.obtener_totales_movimientos_input_dto import (
    ObtenerTotalesMovimientosInputDTO,
)
from finanzas.application.obtener_totales_movimientos_use_case.dtos.totales_de_movimientos_output_dto import (
    TotalesDeMovimientosOutputDTO,
)


class IObtenerTotalesMovimientosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerTotalesMovimientosInputDTO) -> TotalesDeMovimientosOutputDTO: ...
