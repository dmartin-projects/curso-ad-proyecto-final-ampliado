# finanzas/application/comprobar_presupuestos_use_case/comprobar_presupuestos_use_case.py (módulos 76 y 87)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from finanzas.application.comprobar_presupuestos_use_case.dtos.comprobar_presupuestos_input_dto import (
    ComprobarPresupuestosInputDTO,
)
from finanzas.application.comprobar_presupuestos_use_case.i_comprobar_presupuestos_use_case import (
    IComprobarPresupuestosUseCase,
)
from finanzas.application.shared.dtos.presupuesto_output_dto import PresupuestoOutputDTO
from finanzas.domain.events.presupuesto_superado_event import PresupuestoSuperadoEvent
from finanzas.domain.repositories.i_presupuesto_command_repository import IPresupuestoCommandRepository


class ComprobarPresupuestosUseCase(IComprobarPresupuestosUseCase):
    """Detecta los presupuestos que acaban de superarse (y rearma los que han vuelto a estar por debajo).

    Lo pide el sistema (una tarea de Celery tras cada cambio de movimientos). La decisión es del dominio
    (Presupuesto.nueva_alerta); la concurrencia, del repositorio (cambiar_alerta es un UPDATE condicional).
    """

    def __init__(
        self, *, presupuestos: IPresupuestoCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo
    ):
        self.presupuestos, self.eventos, self.uow = presupuestos, eventos, uow

    def ejecutar(self, entrada: ComprobarPresupuestosInputDTO) -> list[PresupuestoOutputDTO]:
        superados = []
        with self.uow:
            for presupuesto, gastado in self.presupuestos.con_gastado(entrada.hogar_id, entrada.meses):
                alerta = presupuesto.nueva_alerta(gastado)
                if alerta is None:
                    continue
                if not self.presupuestos.cambiar_alerta(presupuesto.id, de=presupuesto.alerta_enviada, a=alerta):
                    continue  # otro proceso se ha adelantado: él avisa
                presupuesto.alerta_enviada = alerta
                if alerta:
                    superados.append(PresupuestoOutputDTO.desde_bo(presupuesto))
                    self.eventos.publicar(PresupuestoSuperadoEvent(presupuesto.id, gastado))
        return superados
