# finanzas/application/conciliar_movimientos_use_case/conciliar_movimientos_use_case.py — el gasto apuntado a mano "absorbe" la fila del banco (módulo 75) (módulo 88)
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from finanzas.application.conciliar_movimientos_use_case.dtos.conciliar_movimientos_input_dto import (
    ConciliarMovimientosInputDTO,
)
from finanzas.application.conciliar_movimientos_use_case.i_conciliar_movimientos_use_case import (
    IConciliarMovimientosUseCase,
)
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


class ConciliarMovimientosUseCase(IConciliarMovimientosUseCase):
    """Vincula movimientos con filas del banco. Devuelve los que se han conciliado: uno que ya lo estaba con otra
    fila (otro extracto solapado) no se toca, y quien importa decide qué hacer con esa fila (crear un movimiento).

    Sin eventos: la huella no viaja a Kafka ni cambia ningún número del dashboard.
    """

    rol_minimo = Rol.MIEMBRO

    def __init__(self, *, movimientos: IMovimientoCommandRepository, uow: IUnidadDeTrabajo):
        self.movimientos, self.uow = movimientos, uow

    def ejecutar(self, entrada: ConciliarMovimientosInputDTO) -> list[int]:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            libres = [m for m in self.movimientos.obtener_varios(entrada.hogar_id, entrada.huellas) if not m.conciliado]
            for m in libres:
                m.conciliar(entrada.huellas[m.id])
            self.movimientos.guardar_huellas(libres)
        return [m.id for m in libres]
