# finanzas/application/obtener_cuenta_use_case/i_obtener_cuenta_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.obtener_cuenta_use_case.dtos.obtener_cuenta_input_dto import ObtenerCuentaInputDTO
from finanzas.application.shared.dtos.cuenta_con_saldo_output_dto import CuentaConSaldoOutputDTO


class IObtenerCuentaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerCuentaInputDTO) -> CuentaConSaldoOutputDTO | None: ...
