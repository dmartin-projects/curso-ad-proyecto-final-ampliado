# finanzas/application/listar_cuentas_use_case/i_listar_cuentas_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.listar_cuentas_use_case.dtos.listar_cuentas_input_dto import ListarCuentasInputDTO
from finanzas.application.shared.dtos.cuenta_con_saldo_output_dto import CuentaConSaldoOutputDTO


class IListarCuentasUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarCuentasInputDTO) -> list[CuentaConSaldoOutputDTO]: ...
