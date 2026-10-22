# finanzas/application/eliminar_movimiento_use_case/eliminar_movimiento_use_case.py (módulo 87)
from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from finanzas.application.eliminar_movimiento_use_case.dtos.eliminar_movimiento_input_dto import (
    EliminarMovimientoInputDTO,
)
from finanzas.application.eliminar_movimiento_use_case.i_eliminar_movimiento_use_case import (
    IEliminarMovimientoUseCase,
)
from finanzas.domain.events.movimiento_eliminado_event import MovimientoEliminadoEvent
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


class EliminarMovimientoUseCase(IEliminarMovimientoUseCase):
    rol_minimo = Rol.ADMIN  # borrar es más grave que corregir

    def __init__(
        self,
        *,
        movimientos: IMovimientoCommandRepository,
        auditoria: IAuditoria,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.movimientos, self.auditoria, self.eventos, self.uow = movimientos, auditoria, eventos, uow

    def ejecutar(self, entrada: EliminarMovimientoInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            movimiento = self.movimientos.obtener(entrada.hogar_id, entrada.movimiento_id)
            self.auditoria.registrar(Accion.BORRAR, movimiento, entrada.actor.usuario_id)
            self.movimientos.eliminar(movimiento)
            self.eventos.publicar(MovimientoEliminadoEvent(entrada.movimiento_id, movimiento.hogar_id, movimiento.mes))
