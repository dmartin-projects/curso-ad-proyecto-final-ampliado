"""ProcesarTicketUseCase con los fakes (módulo 88): OCR, IA y finanzas son interfaces; aquí, sin nada de eso."""

from decimal import Decimal

import pytest

from tickets.application.procesar_ticket_use_case.dtos.procesar_ticket_input_dto import ProcesarTicketInputDTO
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.events.ticket_terminado_event import TicketTerminadoEvent
from tickets.domain.exceptions.datos_ilegibles_exception import DatosIlegiblesException
from tickets.tests.fakes.extractor_de_datos_fake import datos
from tickets.tests.fakes.lector_de_tickets_fake import TEXTO
from tickets.tests.fakes.mundo import HOGAR, HOY, Mundo

E = EstadoTicket


def test_procesar_lee_extrae_y_apunta_el_gasto_a_nombre_de_quien_lo_subio():
    mundo = Mundo()
    t = mundo.ticket()

    assert mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id)) == E.PROCESADO

    guardado = mundo.tickets.obtener(HOGAR, t.id)
    assert (guardado.intentos, guardado.texto_ocr, len(guardado.lineas)) == (1, TEXTO, 2)
    [gasto] = mundo.gastos.gastos.values()
    assert (gasto["total"], gasto["concepto"], gasto["creado_por"], gasto["revisado"]) == (
        Decimal("4.85"),
        "Mercadona",
        7,
        True,
    )
    assert mundo.extractor.llamadas == [(TEXTO, ["Supermercado", "Ocio"], None)]  # sin imagen: el OCR sirvió
    assert mundo.eventos.de_tipo(TicketTerminadoEvent) == [TicketTerminadoEvent(t.id)]


def test_con_dudas_el_gasto_queda_sin_revisar_y_el_ticket_a_revision():
    mundo = Mundo(respuesta=datos(confianza=0.4))
    t = mundo.ticket()
    assert mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id)) == E.REVISAR
    assert [g["revisado"] for g in mundo.gastos.gastos.values()] == [False]


def test_sin_total_no_hay_gasto_y_sin_fecha_se_usa_la_de_hoy():
    mundo = Mundo(respuesta=datos(total=None, lineas=()))
    assert mundo.procesar.ejecutar(ProcesarTicketInputDTO(mundo.ticket().id)) == E.REVISAR and mundo.gastos.gastos == {}
    mundo = Mundo(respuesta=datos(fecha=None))
    mundo.procesar.ejecutar(ProcesarTicketInputDTO(mundo.ticket().id))
    assert [g["fecha"] for g in mundo.gastos.gastos.values()] == [HOY]


def test_un_ticket_ya_terminado_no_se_procesa_otra_vez():
    mundo = Mundo()
    t = mundo.ticket()
    mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id))
    assert mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id)) is None  # entrega duplicada de la tarea
    assert len(mundo.gastos.gastos) == 1 and mundo.lector.lecturas == 1


def test_un_reintento_no_repite_el_ocr():
    mundo = Mundo(respuesta=ConnectionError("503"))  # un error pasajero: se propaga, la tarea reintentará
    t = mundo.ticket()
    with pytest.raises(ConnectionError):
        mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id))
    mundo.extractor.respuesta = datos()
    assert mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id)) == E.PROCESADO
    assert mundo.lector.lecturas == 1 and mundo.tickets.obtener(HOGAR, t.id).intentos == 2


def test_si_la_ia_responde_algo_inservible_va_a_revision_sin_gasto():
    mundo = Mundo(respuesta=DatosIlegiblesException("La respuesta no contiene un JSON válido"))
    t = mundo.ticket()
    assert mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id)) == E.REVISAR
    guardado = mundo.tickets.obtener(HOGAR, t.id)
    assert "JSON" in guardado.error and mundo.gastos.gastos == {}
    assert mundo.eventos.publicados == [TicketTerminadoEvent(t.id)]


def test_si_falla_al_guardar_no_queda_ni_gasto_ni_aviso():
    mundo = Mundo()
    t = mundo.ticket()

    def roto(ticket):
        raise RuntimeError("la base de datos se ha caído")

    mundo.tickets.guardar = roto
    with pytest.raises(RuntimeError):
        mundo.procesar.ejecutar(ProcesarTicketInputDTO(t.id))
    assert mundo.gastos.gastos == {} and mundo.eventos.publicados == []  # el gasto, con la transacción del ticket
