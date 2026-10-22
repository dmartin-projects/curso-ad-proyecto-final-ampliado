# finanzas/application/obtener_cuenta_use_case/obtener_cuenta_use_case.py (módulo 87)
from core.domain.enums.rol import Rol
from finanzas.application.obtener_cuenta_use_case.dtos.obtener_cuenta_input_dto import ObtenerCuentaInputDTO
from finanzas.application.obtener_cuenta_use_case.i_obtener_cuenta_use_case import IObtenerCuentaUseCase
from finanzas.application.shared.dtos.cuenta_con_saldo_output_dto import CuentaConSaldoOutputDTO
from finanzas.domain.repositories.i_cuenta_query_service import ICuentaQueryService


class ObtenerCuentaUseCase(IObtenerCuentaUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, cuentas: ICuentaQueryService):
        self.cuentas = cuentas

    def ejecutar(self, entrada: ObtenerCuentaInputDTO) -> CuentaConSaldoOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        leida = self.cuentas.detalle(entrada.hogar_id, entrada.cuenta_id)
        return None if leida is None else CuentaConSaldoOutputDTO.desde_read_model(leida)
