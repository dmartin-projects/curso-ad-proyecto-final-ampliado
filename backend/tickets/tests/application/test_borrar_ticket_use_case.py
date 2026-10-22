"""BorrarTicketUseCase con los fakes (módulo 88)."""

import pytest

from tickets.application.borrar_ticket_use_case.dtos.borrar_ticket_input_dto import BorrarTicketInputDTO
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.events.ticket_borrado_event import TicketBorradoEvent
from tickets.domain.exceptions.ticket_no_encontrado_exception import TicketNoEncontradoException
from tickets.tests.fakes.mundo import HOGAR, OTRO_HOGAR, Mundo, actor

E = EstadoTicket


def test_borrar_y_tickets_de_otro_hogar():
    mundo = Mundo()
    ajeno = mundo.ticket(hogar_id=OTRO_HOGAR)
    with pytest.raises(TicketNoEncontradoException):
        mundo.borrar.ejecutar(BorrarTicketInputDTO(HOGAR, actor(), ajeno.id))
    t = mundo.ticket()
    mundo.borrar.ejecutar(BorrarTicketInputDTO(HOGAR, actor(), t.id))
    assert mundo.eventos.publicados == [TicketBorradoEvent(t.archivo)]  # el archivo, cuando se confirme
