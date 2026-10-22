# finanzas/application/listar_cuentas_use_case/listar_cuentas_use_case.py (módulo 87)
from core.domain.enums.rol import Rol
from core.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery
from finanzas.application.listar_cuentas_use_case.dtos.listar_cuentas_input_dto import ListarCuentasInputDTO
from finanzas.application.listar_cuentas_use_case.i_listar_cuentas_use_case import IListarCuentasUseCase
from finanzas.application.shared.dtos.cuenta_con_saldo_output_dto import CuentaConSaldoOutputDTO
from finanzas.domain.repositories.i_cuenta_query_service import ICuentaQueryService


class ListarCuentasUseCase(IListarCuentasUseCase):
    """Un use case de CONSULTA: sin transacción ni eventos; pide al query service y traduce a OutputDTOs."""

    rol_minimo = Rol.LECTOR

    def __init__(self, *, cuentas: ICuentaQueryService):
        self.cuentas = cuentas

    def ejecutar(self, entrada: ListarCuentasInputDTO) -> list[CuentaConSaldoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        leidas = self.cuentas.listar(ListadoDelHogarQuery(entrada.hogar_id, entrada.orden))
        return [CuentaConSaldoOutputDTO.desde_read_model(c) for c in leidas]
