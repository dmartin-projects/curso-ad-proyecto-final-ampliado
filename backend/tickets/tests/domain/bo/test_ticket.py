"""El ticket y sus transiciones (módulo 88), sin base de datos."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from tickets.domain.bo.ticket import Ticket
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.exceptions.estado_no_permitido_exception import EstadoNoPermitidoException
from tickets.domain.vo.datos_ticket import DatosTicket
from tickets.domain.vo.lectura import Lectura

HOY = date(2026, 10, 15)
AHORA = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)
E = EstadoTicket


def datos(**cambios):
    base = {"comercio": "Mercadona", "fecha": date(2026, 10, 12), "total": Decimal("4.85"), "confianza": 0.93}
    return DatosTicket(**base | cambios)


def ticket(estado=E.PROCESANDO, **extra):
    return Ticket(
        hogar_id=1,
        cuenta_id=1,
        nombre_original="t.jpg",
        tipo_archivo="image/jpeg",
        huella_archivo="h",
        estado=estado,
        **extra,
    )


def test_aplicar_con_y_sin_motivos():
    t = ticket()
    t.aplicar(datos(confianza=0.934), [], movimiento_id=5, ahora=AHORA)
    assert (t.estado, t.confianza, t.movimiento_id, t.error) == (E.PROCESADO, Decimal("0.93"), 5, "")
    t = ticket()
    t.aplicar(datos(total=None), ["No se ha encontrado el total."], movimiento_id=None, ahora=AHORA)
    assert (t.estado, t.error) == (E.REVISAR, "No se ha encontrado el total.")
    with pytest.raises(EstadoNoPermitidoException):  # ya no se está procesando: no se aplica dos veces
        t.aplicar(datos(), [], movimiento_id=6, ahora=AHORA)


def test_confirmar_y_reprocesar_solo_desde_sus_estados():
    with pytest.raises(EstadoNoPermitidoException):
        ticket(E.PROCESADO).confirmar()
    t = ticket(E.REVISAR, movimiento_id=9, texto_ocr="algo", intentos=2)
    assert t.reprocesar(repetir_ocr=True) == 9  # el gasto que tenía: quien reprocesa decide si se descarta
    assert (t.estado, t.intentos, t.movimiento_id, t.texto_ocr) == (E.PENDIENTE, 0, None, "")
    with pytest.raises(EstadoNoPermitidoException):
        ticket(E.PROCESANDO).reprocesar()


def test_el_texto_del_ocr_se_reutiliza_si_era_util():
    assert not Lectura("TOTAL 4,85").es_util and Lectura("x" * 40).es_util
    assert ticket(texto_ocr="x" * 40).texto_reutilizable and not ticket(texto_ocr="  ").texto_reutilizable
