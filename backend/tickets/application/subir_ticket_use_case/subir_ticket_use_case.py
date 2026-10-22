# tickets/application/subir_ticket_use_case/subir_ticket_use_case.py (módulos 74 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from tickets.application.ports.i_gastos import IGastos
from tickets.application.shared.dtos.ticket_output_dto import TicketOutputDTO
from tickets.application.subir_ticket_use_case.dtos.subir_ticket_input_dto import SubirTicketInputDTO
from tickets.application.subir_ticket_use_case.i_subir_ticket_use_case import ISubirTicketUseCase
from tickets.domain.bo.ticket import Ticket
from tickets.domain.events.ticket_pendiente_event import TicketPendienteEvent
from tickets.domain.exceptions.cuenta_no_encontrada_exception import CuentaNoEncontradaException
from tickets.domain.repositories.i_ticket_command_repository import ITicketCommandRepository


class SubirTicketUseCase(ISubirTicketUseCase):
    rol_minimo = Rol.MIEMBRO

    def __init__(
        self, *, tickets: ITicketCommandRepository, gastos: IGastos, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo
    ):
        self.tickets, self.gastos, self.eventos, self.uow = tickets, gastos, eventos, uow

    def ejecutar(self, entrada: SubirTicketInputDTO) -> TicketOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        ticket = Ticket(
            hogar_id=entrada.hogar_id,
            cuenta_id=entrada.cuenta_id,
            subido_por_id=entrada.actor.usuario_id,
            nombre_original=entrada.nombre_original[:200],
            tipo_archivo=entrada.tipo_archivo,
            huella_archivo=entrada.huella_archivo,
        )
        with self.uow:
            if not self.gastos.existe_cuenta(entrada.hogar_id, entrada.cuenta_id):
                raise CuentaNoEncontradaException()
            self.tickets.crear(ticket, entrada.contenido)
            self.eventos.publicar(TicketPendienteEvent(ticket.id))  # el OCR y la IA, en segundo plano, al confirmar
        return TicketOutputDTO.desde_bo(ticket)
