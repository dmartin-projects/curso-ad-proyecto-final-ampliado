"""TerminarSinGastoUseCase con los fakes (módulo 88)."""

from tickets.application.terminar_sin_gasto_use_case.dtos.terminar_sin_gasto_input_dto import TerminarSinGastoInputDTO
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.events.ticket_terminado_event import TicketTerminadoEvent
from tickets.tests.fakes.mundo import Mundo

E = EstadoTicket


def test_terminar_sin_gasto_solo_si_no_estaba_terminado():
    mundo = Mundo()
    t = mundo.ticket(E.PROCESANDO)
    assert mundo.terminar.ejecutar(TerminarSinGastoInputDTO(t.id, "CircuitoAbiertoException: ia")) == E.ERROR
    assert mundo.terminar.ejecutar(TerminarSinGastoInputDTO(t.id, "otra vez")) is None
    assert mundo.eventos.publicados == [TicketTerminadoEvent(t.id)]
