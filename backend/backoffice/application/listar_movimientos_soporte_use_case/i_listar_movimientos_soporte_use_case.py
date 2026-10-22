# backoffice/application/listar_movimientos_soporte_use_case/i_listar_movimientos_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.listar_movimientos_soporte_use_case.dtos.listar_movimientos_soporte_input_dto import (
    ListarMovimientosSoporteInputDTO,
)
from backoffice.application.shared.dtos.movimiento_soporte_output_dto import MovimientoSoporteOutputDTO
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class IListarMovimientosSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarMovimientosSoporteInputDTO) -> PaginaOutputDTO[MovimientoSoporteOutputDTO]: ...
