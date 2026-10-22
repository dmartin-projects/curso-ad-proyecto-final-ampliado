# tickets/application/confirmar_ticket_use_case/confirmar_ticket_use_case.py (módulos 74 y 88)
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from tickets.application.confirmar_ticket_use_case.dtos.confirmar_ticket_input_dto import ConfirmarTicketInputDTO
from tickets.application.confirmar_ticket_use_case.i_confirmar_ticket_use_case import IConfirmarTicketUseCase
from tickets.application.ports.i_gastos import IGastos
from tickets.application.shared.dtos.ticket_output_dto import TicketOutputDTO
from tickets.domain.repositories.i_ticket_command_repository import ITicketCommandRepository


class ConfirmarTicketUseCase(IConfirmarTicketUseCase):
    """La persona revisa (y corrige) lo que propuso la IA: el gasto queda corregido y revisado, o se crea si el
    ticket no tenía total. Lo audita finanzas: es un cambio de un movimiento hecho por una persona."""

    rol_minimo = Rol.MIEMBRO

    def __init__(self, *, tickets: ITicketCommandRepository, gastos: IGastos, uow: IUnidadDeTrabajo):
        self.tickets, self.gastos, self.uow = tickets, gastos, uow

    def ejecutar(self, entrada: ConfirmarTicketInputDTO) -> TicketOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            ticket = self.tickets.obtener(entrada.hogar_id, entrada.ticket_id, bloquear=True)
            ticket.confirmar()
            gasto = {
                "fecha": entrada.fecha,
                "total": entrada.total,
                "concepto": entrada.concepto,
                "categoria_id": entrada.categoria_id,
            }
            if ticket.movimiento_id is not None:
                self.gastos.corregir(
                    hogar_id=entrada.hogar_id, actor=entrada.actor, movimiento_id=ticket.movimiento_id, **gasto
                )
            else:
                ticket.movimiento_id = self.gastos.registrar(
                    hogar_id=entrada.hogar_id, actor=entrada.actor, cuenta_id=ticket.cuenta_id, **gasto
                )
            self.tickets.guardar(ticket)
        return TicketOutputDTO.desde_bo(ticket)
