# finanzas/application/eliminar_movimientos_use_case/eliminar_movimientos_use_case.py — borrar en bloque (módulo 88)
from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from finanzas.application.eliminar_movimientos_use_case.dtos.eliminar_movimientos_input_dto import (
    EliminarMovimientosInputDTO,
)
from finanzas.application.eliminar_movimientos_use_case.i_eliminar_movimientos_use_case import (
    IEliminarMovimientosUseCase,
)
from finanzas.domain.events.movimientos_eliminados_event import MovimientosEliminadosEvent
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


class EliminarMovimientosUseCase(IEliminarMovimientosUseCase):
    """Varios de una vez (deshacer una importación). Las mismas reglas que EliminarMovimientoUseCase: admin, y se
    audita cada uno (en un INSERT)."""

    rol_minimo = Rol.ADMIN

    def __init__(
        self,
        *,
        movimientos: IMovimientoCommandRepository,
        auditoria: IAuditoria,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.movimientos, self.auditoria, self.eventos, self.uow = movimientos, auditoria, eventos, uow

    def ejecutar(self, entrada: EliminarMovimientosInputDTO) -> list[int]:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            borrar = self.movimientos.obtener_varios(entrada.hogar_id, entrada.ids)
            if not borrar:
                return []
            ids = tuple(m.id for m in borrar)
            self.auditoria.registrar_varios(Accion.BORRAR, borrar, entrada.actor.usuario_id)
            self.movimientos.eliminar_varios(entrada.hogar_id, ids)
            self.eventos.publicar(MovimientosEliminadosEvent(entrada.hogar_id, ids, frozenset(m.mes for m in borrar)))
        return list(ids)
