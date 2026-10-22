"""El relay (módulo 85): publica en orden, marca solo lo confirmado y reintenta lo que falla."""

import json
import uuid
from datetime import date
from decimal import Decimal

import pytest

from conftest import CuentaFactory
from core.domain.vo.actor import Actor
from eventos.domain.exceptions.publicacion_no_confirmada_exception import PublicacionNoConfirmadaException
from eventos.domain.services.mensajes import MOVIMIENTOS
from eventos.infrastructure.relay import publicar_lote as relay
from eventos.models import EventoPendiente
from finanzas.application.eliminar_movimiento_use_case.dtos.eliminar_movimiento_input_dto import (
    EliminarMovimientoInputDTO,
)
from finanzas.application.modificar_movimiento_use_case.dtos.modificar_movimiento_input_dto import (
    ModificarMovimientoInputDTO,
)
from finanzas.application.registrar_movimiento_use_case.dtos.registrar_movimiento_input_dto import (
    RegistrarMovimientoInputDTO,
)
from finanzas.infrastructure import container as finanzas

pytestmark = pytest.mark.django_db


class ProductorFalso:
    """Lo mínimo de confluent_kafka.Producer: guarda los mensajes y confirma (o no) al hacer flush()."""

    def __init__(self, falla=False):
        self.mensajes, self.falla, self._pendientes = [], falla, []

    def produce(self, topic, key, value, headers, on_delivery):
        self.mensajes.append({"topic": topic, "key": key, "value": value, "headers": dict(headers)})
        self._pendientes.append(on_delivery)

    def poll(self, timeout):
        return 0

    def flush(self, timeout=None):
        for avisar in self._pendientes:
            avisar("broker caído" if self.falla else None, None)
        self._pendientes = []
        return 0


@pytest.fixture
def tres_eventos(db):
    cuenta = CuentaFactory()
    hogar_id, sistema = cuenta.hogar_id, Actor.sistema()
    EventoPendiente.objects.all().delete()
    m = finanzas.registrar_movimiento().ejecutar(
        RegistrarMovimientoInputDTO(hogar_id, sistema, cuenta.pk, date(2026, 10, 1), Decimal("-10"), "Pan")
    )
    finanzas.modificar_movimiento().ejecutar(
        ModificarMovimientoInputDTO(hogar_id, sistema, m.id, {"importe": Decimal("-1")})
    )
    finanzas.eliminar_movimiento().ejecutar(EliminarMovimientoInputDTO(hogar_id, sistema, m.id))
    return list(EventoPendiente.objects.order_by("id"))


def test_publica_en_orden_con_cabeceras_y_marca(tres_eventos):
    kafka = ProductorFalso()
    assert relay.publicar_lote(kafka) == 3
    claves = {m["key"] for m in kafka.mensajes}
    assert len(claves) == 1  # misma clave: Kafka los pondrá en la misma partición, en este orden
    assert [m["headers"]["tipo"] for m in kafka.mensajes] == [
        "movimiento.creado",
        "movimiento.actualizado",
        "movimiento.eliminado",
    ]
    assert [int(m["headers"]["version"]) for m in kafka.mensajes] == [e.pk for e in tres_eventos]
    assert kafka.mensajes[0]["headers"]["esquema"] == "1"
    assert json.loads(kafka.mensajes[1]["value"])["importe"] == "-1.00"
    assert kafka.mensajes[2]["value"] is None  # tombstone
    assert not EventoPendiente.objects.filter(publicado__isnull=True).exists()
    assert relay.publicar_lote(kafka) == 0  # ya no queda nada


def test_si_kafka_no_confirma_no_se_marca_nada(tres_eventos):
    with pytest.raises(PublicacionNoConfirmadaException):
        relay.publicar_lote(ProductorFalso(falla=True))
    assert EventoPendiente.objects.filter(publicado__isnull=True).count() == 3  # se reintentará entero
    kafka = ProductorFalso()
    assert relay.publicar_lote(kafka) == 3  # Kafka vuelve: sale todo, en el mismo orden


def test_lotes(tres_eventos):
    kafka = ProductorFalso()
    assert relay.publicar_lote(kafka, tamano=2) == 2
    assert relay.publicar_lote(kafka, tamano=2) == 1
    assert [int(m["headers"]["version"]) for m in kafka.mensajes] == [e.pk for e in tres_eventos]


def test_la_traza_viaja_en_la_cabecera(tres_eventos, telemetria):
    from opentelemetry import trace

    cuenta = CuentaFactory()
    entrada = RegistrarMovimientoInputDTO(
        cuenta.hogar_id, Actor.sistema(), cuenta.pk, date(2026, 10, 1), Decimal("-3"), "Pan"
    )
    with trace.get_tracer("test").start_as_current_span("POST /movimientos/") as peticion:
        m = finanzas.registrar_movimiento().ejecutar(entrada)  # el outbox guarda la traza de quien hace el cambio
    ev = EventoPendiente.objects.get(clave=str(m.id), tipo="movimiento.creado")
    assert f"{peticion.get_span_context().trace_id:032x}" in ev.traceparent

    kafka = ProductorFalso()
    relay.publicar_lote(kafka)
    [publicar] = [
        s
        for s in telemetria.spans(f"publish {MOVIMIENTOS}")
        if s.attributes["messaging.kafka.message.key"] == str(m.id)
    ]
    assert publicar.context.trace_id == peticion.get_span_context().trace_id  # misma traza que la petición
    cabecera = next(x["headers"]["traceparent"] for x in kafka.mensajes if x["key"] == str(m.id).encode())
    assert f"{publicar.context.span_id:016x}" in cabecera  # el consumidor colgará del span de publicación


def test_el_sondeo_no_deja_trazas(telemetria):
    """El relay pregunta cada 0,5 s: sin suppress_instrumentation(), 172.800 trazas "SELECT" al día en Tempo."""
    EventoPendiente.objects.all().delete()
    antes = {id(s) for s in telemetria.spans()}
    for _ in range(3):
        assert relay.publicar_lote(ProductorFalso()) == 0
    nuevos = [s for s in telemetria.spans() if id(s) not in antes]
    assert [
        (s.name, s.attributes.get("db.statement", s.attributes.get("db.query.text", ""))[:60]) for s in nuevos
    ] == []


# ── Contra un Kafka de verdad (docker compose -f compose.yaml -f compose.eventos.yaml up -d kafka) ──
def kafka_disponible() -> bool:
    from confluent_kafka.admin import AdminClient
    from django.conf import settings

    try:
        AdminClient({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS}).list_topics(timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False


@pytest.fixture
def topic_temporal():
    """Un topic de usar y tirar con 3 particiones, para no mezclarse con los datos de desarrollo."""
    from confluent_kafka.admin import AdminClient, NewTopic

    admin = AdminClient({"bootstrap.servers": "localhost:9092"})
    nombre = f"test.movimientos.{uuid.uuid4().hex[:8]}"
    admin.create_topics([NewTopic(nombre, num_partitions=3, replication_factor=1)])[nombre].result()
    yield nombre
    admin.delete_topics([nombre])[nombre].result()


@pytest.mark.skipif(not kafka_disponible(), reason="sin Kafka en localhost:9092")
def test_contra_kafka_de_verdad(tres_eventos, topic_temporal):
    import time

    from confluent_kafka import Consumer

    from eventos.infrastructure.messaging.kafka import productor

    EventoPendiente.objects.update(topic=topic_temporal)
    assert relay.publicar_lote(productor()) == 3

    consumidor = Consumer({"bootstrap.servers": "localhost:9092", "group.id": f"test-{uuid.uuid4()}",
                           "auto.offset.reset": "earliest", "enable.auto.commit": False})  # fmt: skip
    consumidor.subscribe([topic_temporal])
    leidos, limite = [], time.monotonic() + 30
    while len(leidos) < 3 and time.monotonic() < limite:
        msg = consumidor.poll(1)
        if msg is not None and not msg.error():
            leidos.append(msg)
    consumidor.close()

    assert [dict(m.headers())["tipo"] for m in leidos] == [
        b"movimiento.creado",
        b"movimiento.actualizado",
        b"movimiento.eliminado",
    ]
    assert len({m.partition() for m in leidos}) == 1  # misma clave → las tres en la MISMA partición
    assert leidos[0].offset() < leidos[1].offset() < leidos[2].offset()  # y en orden
    assert leidos[2].value() is None  # el tombstone llega como valor nulo
