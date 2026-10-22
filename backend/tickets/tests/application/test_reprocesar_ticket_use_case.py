"""ReprocesarTicketUseCase con los fakes (módulo 88)."""

import pytest

from core.domain.enums.accion import Accion
from tickets.application.procesar_ticket_use_case.dtos.procesar_ticket_input_dto import ProcesarTicketInputDTO
from tickets.application.reprocesar_ticket_use_case.dtos.reprocesar_ticket_input_dto import ReprocesarTicketInputDTO
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.events.ticket_pendiente_event import TicketPendienteEvent
from tickets.domain.exceptions.estado_no_permitido_exception import EstadoNoPermitidoException
from tickets.tests.fakes.extractor_de_datos_fake import datos
from tickets.tests.fakes.mundo import HOGAR, Mundo, actor

E = EstadoTicket


def test_reprocesar_descarta_el_gasto_sin_revisar_audita_y_pide_procesarlo():
    mundo = Mundo(respuesta=datos(confianza=0.4))
    t = mundo.ticket()
    mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id))
    mundo.eventos.publicados.clear()

    mundo.reprocesar.ejecutar(ReprocesarTicketInputDTO(HOGAR, actor(), t.id))

    assert mundo.gastos.gastos == {}
    [(accion, tipo, pk, usuario, cambios)] = mundo.auditoria.registros
    assert (accion, tipo, pk, usuario) == (Accion.MODIFICAR, "tickets.ticket", t.id, 7)
    assert cambios["estado"] == ["revisar", "pendiente"]
    assert mundo.eventos.publicados == [TicketPendienteEvent(t.id)]
    with pytest.raises(EstadoNoPermitidoException):
        mundo.reprocesar.ejecutar(ReprocesarTicketInputDTO(HOGAR, actor(), t.id))  # pendiente: no


def test_reprocesar_no_toca_un_gasto_ya_revisado():
    mundo = Mundo()
    t = mundo.ticket()
    mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id))  # procesado y revisado… y luego alguien lo pasa a error
    guardado = mundo.tickets.obtener(HOGAR, t.id)
    guardado.estado = E.ERROR
    mundo.tickets.guardar(guardado)
    mundo.reprocesar.ejecutar(ReprocesarTicketInputDTO(HOGAR, actor(), t.id))
    assert len(mundo.gastos.gastos) == 1
