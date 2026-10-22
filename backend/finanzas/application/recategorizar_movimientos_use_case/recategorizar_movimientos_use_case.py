# finanzas/application/recategorizar_movimientos_use_case/recategorizar_movimientos_use_case.py (módulo 87)
from dataclasses import replace

from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from finanzas.application.recategorizar_movimientos_use_case.dtos.recategorizar_movimientos_input_dto import (
    RecategorizarMovimientosInputDTO,
)
from finanzas.application.recategorizar_movimientos_use_case.i_recategorizar_movimientos_use_case import (
    IRecategorizarMovimientosUseCase,
)
from finanzas.application.shared.autorizacion_por_hogar import exigir_categoria
from finanzas.domain.bo.movimiento import Movimiento
from finanzas.domain.events.movimientos_recategorizados_event import MovimientosRecategorizadosEvent
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


class RecategorizarMovimientosUseCase(IRecategorizarMovimientosUseCase):
    """Hasta 1.000 movimientos de una vez: un UPDATE, no 1.000 BOs guardados (no castrar el ORM).
    La regla ("elegir la categoría es revisarlo") sigue siendo del dominio: cambios_al_recategorizar.

    Se audita uno a uno (en un solo INSERT), como cualquier modificación de un movimiento.
    """

    rol_minimo = Rol.MIEMBRO

    def __init__(
        self,
        *,
        movimientos: IMovimientoCommandRepository,
        categorias: ICategoriaCommandRepository,
        auditoria: IAuditoria,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.movimientos, self.categorias, self.auditoria = movimientos, categorias, auditoria
        self.eventos, self.uow = eventos, uow

    def ejecutar(self, entrada: RecategorizarMovimientosInputDTO) -> int:
        entrada.actor.exigir(self.rol_minimo)
        cambios = Movimiento.cambios_al_recategorizar(entrada.categoria_id)
        with self.uow:
            exigir_categoria(self.categorias, entrada.hogar_id, entrada.categoria_id, "categoria")
            antes = self.movimientos.obtener_varios(entrada.hogar_id, entrada.ids)  # para la auditoría: un SELECT
            ids, meses = self.movimientos.actualizar_en_bloque(entrada.hogar_id, [m.id for m in antes], cambios)
            antes = [m for m in antes if m.id in set(ids)]  # por si otro lo ha borrado entre medias
            despues = [replace(m, **cambios) for m in antes]  # replace() vuelve a pasar por __post_init__
            self.auditoria.registrar_varios(Accion.MODIFICAR, despues, entrada.actor.usuario_id, antes=antes)
            if ids:
                self.eventos.publicar(MovimientosRecategorizadosEvent(entrada.hogar_id, tuple(ids), frozenset(meses)))
        return len(ids)
