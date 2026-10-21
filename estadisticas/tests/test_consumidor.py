"""El consumidor contra un Kafka de verdad (módulo 85): orden, offsets, fallos y reconstrucción."""

import json
import threading
import time
import uuid

import pytest
from sqlalchemy import func, select

from estadisticas import consumidor
from estadisticas.ajustes import ajustes
from estadisticas.bd import Movimiento, Progreso, sesion


def kafka_disponible() -> bool:
    from confluent_kafka.admin import AdminClient

    try:
        AdminClient({"bootstrap.servers": "localhost:9092"}).list_topics(timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = [pytest.mark.kafka, pytest.mark.skipif(not kafka_disponible(), reason="sin Kafka en localhost:9092")]


@pytest.fixture
def topics(monkeypatch):
    """Topics y grupo de usar y tirar: un test NUNCA escribe en los topics de desarrollo (ver el módulo 85)."""
    from confluent_kafka.admin import AdminClient, NewTopic

    admin = AdminClient({"bootstrap.servers": "localhost:9092"})
    sufijo = uuid.uuid4().hex[:8]
    movs, membs = f"test.movimientos.{sufijo}", f"test.membresias.{sufijo}"
    for f in admin.create_topics([NewTopic(movs, 3, 1), NewTopic(membs, 1, 1)]).values():
        f.result()
    a = ajustes()
    monkeypatch.setattr(a, "topic_movimientos", movs)
    monkeypatch.setattr(a, "topic_membresias", membs)
    monkeypatch.setattr(a, "kafka_grupo", f"test-{sufijo}")
    yield movs
    for f in admin.delete_topics([movs, membs]).values():
        f.result()


def publicar(topic, eventos):
    """eventos: [(id, importe o None, version)] con el formato que publica el relay de Django."""
    from confluent_kafka import Producer

    p = Producer({"bootstrap.servers": "localhost:9092"})
    for pk, importe, version in eventos:
        valor = (
            None
            if importe is None
            else json.dumps(
                {
                    "id": pk,
                    "hogar_id": 1,
                    "cuenta_id": 1,
                    "fecha": "2026-10-01",
                    "importe": importe,
                    "categoria_id": None,
                    "comercio_id": None,
                    "origen": "manual",
                }  # fmt: skip
            ).encode()
        )
        p.produce(topic, key=str(pk).encode(), value=valor, headers=[("version", str(version)), ("esquema", "1")])
    assert p.flush(10) == 0


def en_marcha():
    """Arranca el consumidor en un hilo; devuelve la función para pararlo."""
    parar = threading.Event()
    hilo = threading.Thread(target=consumidor.ejecutar, args=(parar,), daemon=True)
    hilo.start()

    def _parar():
        parar.set()
        hilo.join(15)

    return _parar


def esperar(condicion, segundos=30):
    limite = time.monotonic() + segundos
    while time.monotonic() < limite:
        if condicion():
            return True
        time.sleep(0.2)
    return False


def filas():
    with sesion() as s:
        return dict(s.execute(select(Movimiento.id, Movimiento.importe)).all())


def test_aplica_en_orden_y_confirma_offsets(topics):
    # 20 movimientos con tres versiones cada uno: si el orden por clave fallara, quedaría alguna vieja
    eventos = [(pk, f"-{v}.00", pk * 10 + v) for v in (1, 2, 3) for pk in range(1, 21)]
    eventos += [(pk, None, pk * 10 + 4) for pk in range(1, 6)]  # y 5 borrados
    publicar(topics, eventos)
    parar = en_marcha()
    try:
        assert esperar(lambda: len(filas()) == 15 and set(map(str, filas().values())) == {"-3.00"})
    finally:
        parar()
    with sesion() as s:  # el progreso guardado cubre las 3 particiones
        assert s.scalar(select(func.count()).select_from(Progreso).where(Progreso.topic == topics)) == 3

    # Los offsets confirmados: al volver a arrancar NO se relee nada (y si se releyera, daría igual)
    from confluent_kafka import Consumer

    c = Consumer({"bootstrap.servers": "localhost:9092", "group.id": ajustes().kafka_grupo})
    from confluent_kafka import TopicPartition

    confirmados = c.committed([TopicPartition(topics, p) for p in range(3)], timeout=10)
    c.close()
    assert sum(tp.offset for tp in confirmados) == len(eventos)


def test_si_falla_la_bd_rebobina_y_no_pierde_nada(topics, monkeypatch):
    publicar(topics, [(pk, "-1.00", pk) for pk in range(1, 11)])
    original, fallos = consumidor.aplicar, []

    def a_veces_falla(*args):
        if len(fallos) < 2:  # los dos primeros intentos de lote: "PostgreSQL caído"
            fallos.append(1)
            raise ConnectionError("PostgreSQL no responde")
        return original(*args)

    monkeypatch.setattr(consumidor, "aplicar", a_veces_falla)
    parar = en_marcha()
    try:
        # Sin _rebobinar(), los mensajes del lote fallido se saltaban: quedaban menos de 10 filas
        assert esperar(lambda: len(filas()) == 10, segundos=40), filas()
    finally:
        parar()
    assert len(fallos) == 2


def test_reconstruir_desde_el_principio(topics, monkeypatch):
    publicar(topics, [(pk, "-5.00", pk) for pk in range(1, 6)])
    parar = en_marcha()
    try:
        assert esperar(lambda: len(filas()) == 5)
    finally:
        parar()
    from estadisticas import reconstruir

    reconstruir.reconstruir()  # vacía las tablas y borra el grupo: el próximo arranque lee desde el offset 0
    assert filas() == {}
    parar = en_marcha()
    try:
        assert esperar(lambda: len(filas()) == 5)
    finally:
        parar()
