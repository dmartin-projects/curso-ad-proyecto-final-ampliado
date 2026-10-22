# finanzas/application/descartar_propuestos_use_case/descartar_propuestos_use_case.py — el gasto que propuso un proceso, si nadie lo ha revisado (módulo 88)
from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from finanzas.application.descartar_propuestos_use_case.dtos.descartar_propuestos_input_dto import (
    DescartarPropuestosInputDTO,
)
from finanzas.application.descartar_propuestos_use_case.i_descartar_propuestos_use_case import (
    IDescartarPropuestosUseCase,
)
from finanzas.domain.events.movimientos_eliminados_event import MovimientosEliminadosEvent
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


class DescartarPropuestosUseCase(IDescartarPropuestosUseCase):
    """Reprocesar un ticket descarta el gasto que propuso… si nadie lo ha revisado (módulos 74 y 88).

    La misma orquestación que EliminarMovimientosUseCase (auditar, borrar, publicar) con otra regla: un miembro
    puede, porque ese gasto aún no es un dato de nadie (Movimiento.es_propuesta). Uno revisado no se toca.
    """

    rol_minimo = Rol.MIEMBRO

    def __init__(
        self,
        *,
        movimientos: IMovimientoCommandRepository,
        auditoria: IAuditoria,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.movimientos, self.auditoria, self.eventos, self.uow = movimientos, auditoria, eventos, uow

    def ejecutar(self, entrada: DescartarPropuestosInputDTO) -> list[int]:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            borrar = [m for m in self.movimientos.obtener_varios(entrada.hogar_id, entrada.ids) if m.es_propuesta]
            if not borrar:
                return []
            ids = tuple(m.id for m in borrar)
            self.auditoria.registrar_varios(Accion.BORRAR, borrar, entrada.actor.usuario_id)
            self.movimientos.eliminar_varios(entrada.hogar_id, ids)
            self.eventos.publicar(MovimientosEliminadosEvent(entrada.hogar_id, ids, frozenset(m.mes for m in borrar)))
        return list(ids)
