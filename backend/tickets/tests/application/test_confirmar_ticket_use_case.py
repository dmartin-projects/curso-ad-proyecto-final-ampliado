"""ConfirmarTicketUseCase con los fakes (módulo 88)."""

from datetime import date
from decimal import Decimal

import pytest

from tickets.application.confirmar_ticket_use_case.dtos.confirmar_ticket_input_dto import ConfirmarTicketInputDTO
from tickets.application.procesar_ticket_use_case.dtos.procesar_ticket_input_dto import ProcesarTicketInputDTO
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.exceptions.estado_no_permitido_exception import EstadoNoPermitidoException
from tickets.tests.fakes.extractor_de_datos_fake import datos
from tickets.tests.fakes.mundo import HOGAR, HOY, Mundo, actor

E = EstadoTicket


def test_confirmar_corrige_el_gasto_propuesto_o_lo_crea():
    mundo = Mundo(respuesta=datos(confianza=0.4))
    t = mundo.ticket()
    mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id))
    entrada = ConfirmarTicketInputDTO(
        HOGAR, actor(), t.id, date(2026, 10, 12), Decimal("4.95"), "Mercadona", categoria_id=3
    )

    assert mundo.confirmar.ejecutar(entrada).estado == E.PROCESADO
    [gasto] = mundo.gastos.gastos.values()
    assert (gasto["total"], gasto["revisado"], gasto["categoria_id"]) == (Decimal("4.95"), True, 3)
    with pytest.raises(EstadoNoPermitidoException):
        mundo.confirmar.ejecutar(entrada)  # ya no está en revisión

    sin_total = mundo.ticket(E.REVISAR)
    confirmado = mundo.confirmar.ejecutar(
        ConfirmarTicketInputDTO(HOGAR, actor(), sin_total.id, HOY, Decimal("12.40"), "Bar")
    )
    assert mundo.gastos.gastos[confirmado.movimiento_id]["de"] == "persona"
