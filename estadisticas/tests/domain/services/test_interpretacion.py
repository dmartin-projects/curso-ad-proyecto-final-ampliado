"""interpretar(): qué significa cada mensaje. Formato, lector tolerante y mensajes mal formados (módulo 89). Sin
base de datos."""

import json
from datetime import date
from decimal import Decimal, InvalidOperation

import pytest

from estadisticas.domain.bo.membresia import Membresia
from estadisticas.domain.enums.topic import Topic
from estadisticas.domain.events.membresia_eliminada_event import MembresiaEliminadaEvent
from estadisticas.domain.events.membresia_guardada_event import MembresiaGuardadaEvent
from estadisticas.domain.events.movimiento_eliminado_event import MovimientoEliminadoEvent
from estadisticas.domain.events.movimiento_guardado_event import MovimientoGuardadoEvent
from estadisticas.domain.exceptions.esquema_desconocido_exception import EsquemaDesconocidoException
from estadisticas.domain.exceptions.evento_invalido_exception import EventoInvalidoException
from estadisticas.domain.services.interpretacion import interpretar

CAB = {"version": "7", "esquema": "1"}


def datos(**extra) -> bytes:
    base = {"id": 3, "hogar_id": 1, "cuenta_id": 2, "fecha": "2026-10-01", "importe": "-12.50",
            "categoria_id": 4, "comercio_id": None, "origen": "manual", "revisado": False}  # fmt: skip
    return json.dumps(base | extra).encode()


def test_un_movimiento():
    evento = interpretar(Topic.MOVIMIENTOS, "3", datos(), CAB)
    assert isinstance(evento, MovimientoGuardadoEvent)
    m = evento.movimiento
    assert (m.id, m.fecha, m.importe, m.revisado, m.version) == (3, date(2026, 10, 1), Decimal("-12.50"), False, 7)


def test_un_tombstone_es_un_borrado():
    assert interpretar(Topic.MOVIMIENTOS, "3", None, CAB) == MovimientoEliminadoEvent(3, 7)
    assert interpretar(Topic.MEMBRESIAS, "1:5", None, CAB) == MembresiaEliminadaEvent(1, 5, 7)


def test_una_membresia():
    valor = json.dumps({"hogar_id": 1, "usuario_id": 5, "rol": "lector"}).encode()
    assert interpretar(Topic.MEMBRESIAS, "1:5", valor, CAB) == MembresiaGuardadaEvent(Membresia(1, 5, "lector", 7))


def test_lector_tolerante():
    """Django puede AÑADIR campos sin romper a quien no los usa; y un mensaje antiguo sin "revisado" vale True."""
    assert isinstance(interpretar(Topic.MOVIMIENTOS, "3", datos(etiquetas=["viaje"], moneda="EUR"), CAB),
                      MovimientoGuardadoEvent)  # fmt: skip
    sin_revisado = json.loads(datos())
    del sin_revisado["revisado"]
    evento = interpretar(Topic.MOVIMIENTOS, "3", json.dumps(sin_revisado).encode(), CAB)
    assert evento.movimiento.revisado is True


@pytest.mark.parametrize("esquema", ["2", None])
def test_un_esquema_desconocido_para(esquema):
    cabeceras = {"version": "7"} | ({"esquema": esquema} if esquema else {})
    with pytest.raises(EsquemaDesconocidoException):
        interpretar(Topic.MOVIMIENTOS, "3", datos(), cabeceras)


@pytest.mark.parametrize(
    ("topic", "clave", "valor", "cabeceras", "causa"),
    [
        (Topic.MOVIMIENTOS, "3", b"{esto no es JSON", CAB, json.JSONDecodeError),
        (Topic.MOVIMIENTOS, "3", json.dumps({"id": 3, "importe": "abc"}).encode(), CAB, KeyError),
        (Topic.MOVIMIENTOS, "3", datos(importe="abc"), CAB, InvalidOperation),
        (Topic.MOVIMIENTOS, "3", datos(fecha=None), CAB, TypeError),
        (Topic.MOVIMIENTOS, "tres", datos(), CAB, ValueError),
        (Topic.MOVIMIENTOS, "3", datos(), {"esquema": "1"}, KeyError),  # sin versión
        (Topic.MEMBRESIAS, "1", None, CAB, ValueError),  # la clave es "hogar:usuario"
    ],
)
def test_un_mensaje_mal_formado_es_un_evento_invalido(topic, clave, valor, cabeceras, causa):
    with pytest.raises(EventoInvalidoException) as error:
        interpretar(topic, clave, valor, cabeceras)
    assert type(error.value.causa) is causa  # el error original: es lo que se anota al aparcarlo


def test_un_topic_que_no_es_de_este_servicio():
    assert interpretar(None, "x", datos(), CAB) is None
