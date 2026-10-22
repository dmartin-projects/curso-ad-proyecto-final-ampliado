# tickets/application/reprocesar_ticket_use_case/reprocesar_ticket_use_case.py (módulos 74 y 88)
from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from tickets.application.ports.i_gastos import IGastos
from tickets.application.reprocesar_ticket_use_case.dtos.reprocesar_ticket_input_dto import ReprocesarTicketInputDTO
from tickets.application.reprocesar_ticket_use_case.i_reprocesar_ticket_use_case import IReprocesarTicketUseCase
from tickets.application.shared.dtos.ticket_output_dto import TicketOutputDTO
from tickets.domain.events.ticket_pendiente_event import TicketPendienteEvent
from tickets.domain.repositories.i_ticket_command_repository import ITicketCommandRepository


class ReprocesarTicketUseCase(IReprocesarTicketUseCase):
    """Volver a leer un ticket en revisión o con error. El gasto propuesto se descarta (si nadie lo ha revisado).

    Se audita, lo pida una persona desde la app o el personal de soporte desde el backoffice: los dos llaman a este
    use case.
    """

    rol_minimo = Rol.MIEMBRO

    def __init__(
        self,
        *,
        tickets: ITicketCommandRepository,
        gastos: IGastos,
        auditoria: IAuditoria,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.tickets, self.gastos, self.auditoria, self.eventos, self.uow = tickets, gastos, auditoria, eventos, uow

    def ejecutar(self, entrada: ReprocesarTicketInputDTO) -> TicketOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            ticket = self.tickets.obtener(entrada.hogar_id, entrada.ticket_id, bloquear=True)
            antes = ticket.instantanea()
            gasto = ticket.reprocesar(repetir_ocr=entrada.repetir_ocr)
            if gasto is not None:
                self.gastos.descartar(hogar_id=entrada.hogar_id, actor=entrada.actor, movimiento_id=gasto)
            self.tickets.guardar(ticket)
            self.auditoria.registrar(Accion.MODIFICAR, ticket, entrada.actor.usuario_id, antes=antes)
            self.eventos.publicar(TicketPendienteEvent(ticket.id))
        return TicketOutputDTO.desde_bo(ticket)
