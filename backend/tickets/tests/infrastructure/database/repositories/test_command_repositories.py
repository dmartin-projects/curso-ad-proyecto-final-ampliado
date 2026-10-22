"""Contract tests de los tickets (módulo 88): los mismos tests contra el repositorio ORM y contra el fake.

El lector (OCR) y el extractor (IA) falsos no tienen contract test: no imitan un comportamiento, devuelven lo que
cada test les pide. Sus adapters de verdad tienen sus tests (infrastructure/ocr/, infrastructure/ia/).
"""

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from conftest import CuentaFactory
from tickets.domain.bo.ticket import Ticket
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.exceptions.ticket_no_encontrado_exception import TicketNoEncontradoException
from tickets.domain.exceptions.ticket_repetido_exception import TicketRepetidoException
from tickets.domain.repositories.i_ticket_command_repository import ITicketCommandRepository
from tickets.infrastructure.database.repositories.ticket_command_repository_orm import TicketCommandRepositoryORM
from tickets.tests.fakes.extractor_de_datos_fake import datos
from tickets.tests.fakes.mundo import HOGAR, OTRO_HOGAR
from tickets.tests.fakes.ticket_command_repository_fake import TicketCommandRepositoryFake

E = EstadoTicket
AHORA = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)


@dataclass
class Entorno:
    tickets: ITicketCommandRepository
    hogar: int
    otro_hogar: int
    cuenta: int
    contenido: object


@pytest.fixture(params=["memoria", "orm"])
def entorno(request) -> Entorno:
    if request.param == "memoria":
        return Entorno(TicketCommandRepositoryFake(), HOGAR, OTRO_HOGAR, 10, lambda: b"x")
    request.getfixturevalue("db")
    cuenta, ajena = CuentaFactory(), CuentaFactory()
    return Entorno(
        TicketCommandRepositoryORM(),
        cuenta.hogar_id,
        ajena.hogar_id,
        cuenta.pk,
        lambda: SimpleUploadedFile("t.jpg", b"jpeg", content_type="image/jpeg"),
    )


def nuevo(e: Entorno, huella="h1", hogar=None) -> Ticket:
    t = Ticket(
        hogar_id=hogar or e.hogar,
        cuenta_id=e.cuenta,
        nombre_original="t.jpg",
        tipo_archivo="image/jpeg",
        huella_archivo=huella,
    )
    e.tickets.crear(t, e.contenido())
    return t


def test_crear_obtener_y_repetido(entorno):
    t = nuevo(entorno)
    assert t.id and t.archivo and entorno.tickets.leer_archivo(t) in (b"jpeg", b"x")
    assert entorno.tickets.obtener(entorno.hogar, t.id).estado == E.PENDIENTE
    with pytest.raises(TicketNoEncontradoException):
        entorno.tickets.obtener(entorno.otro_hogar, t.id)
    with pytest.raises(TicketRepetidoException):
        nuevo(entorno, huella="h1")
    assert nuevo(entorno, huella="h2").id  # tras el error, se puede seguir guardando (savepoint)


def test_reclamar_es_condicional(entorno):
    t = nuevo(entorno)
    assert entorno.tickets.reclamar(t.id).intentos == 1
    assert entorno.tickets.reclamar(t.id).intentos == 2  # procesando: un reintento puede seguir
    assert entorno.tickets.terminar_sin_gasto(t.id, E.ERROR, "boom", AHORA) is True
    assert entorno.tickets.reclamar(t.id) is None  # terminado: nada que hacer
    assert entorno.tickets.terminar_sin_gasto(t.id, E.REVISAR, "otra", AHORA) is False


def test_guardar_el_resultado_con_sus_lineas(entorno):
    t = nuevo(entorno)
    entorno.tickets.reclamar(t.id)
    entorno.tickets.guardar_texto(t.id, "TOTAL 4,85")
    t = entorno.tickets.bloquear(t.id)
    t.aplicar(datos(), [], None, AHORA)
    entorno.tickets.guardar(t)
    leido = entorno.tickets.obtener(entorno.hogar, t.id)
    assert (leido.estado, leido.texto_ocr, leido.datos, [li.descripcion for li in leido.lineas]) == (
        E.PROCESADO,
        "TOTAL 4,85",
        datos(),  # ida y vuelta: lo que se guarda como JSON se lee igual
        ["Leche", "Pan"],
    )
    entorno.tickets.eliminar(leido)
    with pytest.raises(TicketNoEncontradoException):
        entorno.tickets.obtener(entorno.hogar, t.id)
