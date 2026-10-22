# finanzas/application/eliminar_presupuesto_use_case/eliminar_presupuesto_use_case.py (módulos 76 y 87)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from finanzas.application.eliminar_presupuesto_use_case.dtos.eliminar_presupuesto_input_dto import (
    EliminarPresupuestoInputDTO,
)
from finanzas.application.eliminar_presupuesto_use_case.i_eliminar_presupuesto_use_case import (
    IEliminarPresupuestoUseCase,
)
from finanzas.domain.events.presupuestos_cambiados_event import PresupuestosCambiadosEvent
from finanzas.domain.repositories.i_presupuesto_command_repository import IPresupuestoCommandRepository


class EliminarPresupuestoUseCase(IEliminarPresupuestoUseCase):
    rol_minimo = Rol.ADMIN

    def __init__(
        self, *, presupuestos: IPresupuestoCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo
    ):
        self.presupuestos, self.eventos, self.uow = presupuestos, eventos, uow

    def ejecutar(self, entrada: EliminarPresupuestoInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            presupuesto = self.presupuestos.obtener(entrada.hogar_id, entrada.presupuesto_id)
            self.presupuestos.eliminar(presupuesto)
            # el dashboard deja de enseñar el presupuesto borrado en cuanto se confirma
            self.eventos.publicar(PresupuestosCambiadosEvent(entrada.hogar_id, frozenset({presupuesto.mes})))
