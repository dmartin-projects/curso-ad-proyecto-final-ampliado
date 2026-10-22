# finanzas/application/desconciliar_movimientos_use_case/desconciliar_movimientos_use_case.py (módulo 88)
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from finanzas.application.desconciliar_movimientos_use_case.dtos.desconciliar_movimientos_input_dto import (
    DesconciliarMovimientosInputDTO,
)
from finanzas.application.desconciliar_movimientos_use_case.i_desconciliar_movimientos_use_case import (
    IDesconciliarMovimientosUseCase,
)
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


class DesconciliarMovimientosUseCase(IDesconciliarMovimientosUseCase):
    """Deshacer una importación devuelve los gastos conciliados a como estaban: sin fila del banco."""

    rol_minimo = Rol.MIEMBRO

    def __init__(self, *, movimientos: IMovimientoCommandRepository, uow: IUnidadDeTrabajo):
        self.movimientos, self.uow = movimientos, uow

    def ejecutar(self, entrada: DesconciliarMovimientosInputDTO) -> int:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            conciliados = [m for m in self.movimientos.obtener_varios(entrada.hogar_id, entrada.ids) if m.conciliado]
            for m in conciliados:
                m.desconciliar()
            self.movimientos.guardar_huellas(conciliados)
        return len(conciliados)
