"""El consumidor contra un Kafka de verdad (módulos 85 y 89): orden, offsets, fallos y reconstrucción."""

import json
import threading
import time
import uuid

import pytest
from sqlalchemy import func, select

from estadisticas.ajustes import ajustes
from estadisticas.infrastructure import container
from estadisticas.infrastructure.consumer import consumidor_kafka
from estadisticas.infrastructure.database.models.movimiento_model import MovimientoModel
from estadisticas.infrastructure.database.models.progreso_model import ProgresoModel
from estadisticas.infrastructure.database.repositories.movimiento_command_repository_sql import (
    MovimientoCommandRepositorySQL,
)
from estadisticas.infrastructure.database.sesiones import sesion

KAFKA = {"bootstrap.servers": ajustes().kafka_bootstrap_servers}


def kafka_disponible() -> bool:
    from confluent_kafka.admin import AdminClient

    try:
        AdminClient(KAFKA).list_topics(timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = [pytest.mark.kafka, pytest.mark.skipif(not kafka_disponible(), reason=f"sin Kafka en {KAFKA}")]


@pytest.fixture
def topics(monkeypatch):
    """Topics y grupo de usar y tirar: un test NUNCA escribe en los topics de desarrollo (ver el módulo 85)."""
    from confluent_kafka.admin import AdminClient, NewTopic

    admin = AdminClient(KAFKA)
    sufijo = uuid.uuid4().hex[:8]
    movs, membs = f"test.movimientos.{sufijo}", f"test.membresias.{sufijo}"
    for f in admin.create_topics([NewTopic(movs, 3, 1), NewTopic(membs, 1, 1)]).values():
        f.result()
    a = ajustes()
    monkeypatch.setattr(a, "topic_movimientos", movs)
    monkeypatch.setattr(a, "topic_membresias", membs)
    monkeypatch.setattr(a, "kafka_grupo", f"test-{sufijo}")
    monkeypatch.setattr(a, "topic_dlq", f"test.aparcados.{sufijo}")
    yield movs
    for f in admin.delete_topics([movs, membs, a.topic_dlq]).values():
        try:
            f.result()
        except Exception:  # noqa: BLE001  (el de aparcados solo existe si ha arrancado un consumidor)
            pass


def publicar(topic, eventos):
    """eventos: [(id, importe o None, version)] con el formato que publica el relay de Django."""
    from confluent_kafka import Producer

    p = Producer(KAFKA)
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
    hilo = threading.Thread(target=consumidor_kafka.ejecutar, args=(parar,), daemon=True)
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
        return dict(s.execute(select(MovimientoModel.id, MovimientoModel.importe)).all())


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
        assert s.scalar(select(func.count()).select_from(ProgresoModel).where(ProgresoModel.topic == topics)) == 3

    # Los offsets confirmados: al volver a arrancar NO se relee nada (y si se releyera, daría igual)
    from confluent_kafka import Consumer

    c = Consumer(KAFKA | {"group.id": ajustes().kafka_grupo})
    from confluent_kafka import TopicPartition

    confirmados = c.committed([TopicPartition(topics, p) for p in range(3)], timeout=10)
    c.close()
    assert sum(tp.offset for tp in confirmados) == len(eventos)


def test_si_falla_la_bd_rebobina_y_no_pierde_nada(topics, monkeypatch):
    publicar(topics, [(pk, "-1.00", pk) for pk in range(1, 11)])
    fallos = []

    class FallaDosVeces(MovimientoCommandRepositorySQL):
        def guardar(self, movimiento):
            if len(fallos) < 2:  # los dos primeros intentos de lote: "PostgreSQL caído"
                fallos.append(1)
                raise ConnectionError("PostgreSQL no responde")
            return super().guardar(movimiento)

    # Una pieza del composition root, cambiada para este test: el consumidor no se entera
    monkeypatch.setattr(container, "MovimientoCommandRepositorySQL", FallaDosVeces)
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
    container.reconstruir_proyeccion().ejecutar()  # borra el grupo y vacía las tablas: al arrancar, lee desde el 0
    assert filas() == {}
    parar = en_marcha()
    try:
        assert esperar(lambda: len(filas()) == 5)
    finally:
        parar()


# ── Módulo 85, ejercicio 2: el retraso del consumidor ──
def test_retraso(topics):
    from estadisticas.infrastructure.metrics.retraso_consumidor import retraso

    publicar(topics, [(pk, "-1.00", pk) for pk in range(1, 8)])
    assert retraso()[topics] == 7  # nadie ha leído aún: todo pendiente
    parar = en_marcha()
    try:
        assert esperar(lambda: retraso()[topics] == 0)  # el consumidor ha confirmado hasta el final
    finally:
        parar()
    publicar(topics, [(99, "-1.00", 99)])  # con el consumidor parado, el retraso crece
    assert retraso()[topics] == 1


# ── Módulo 85, ejercicio 3: mensajes venenosos ──
def test_un_mensaje_venenoso_se_aparca_y_no_bloquea_la_particion(topics):
    from confluent_kafka import Consumer, Producer

    p = Producer(KAFKA)
    cab = [("version", "1"), ("esquema", "1")]
    publicar(topics, [(1, "-1.00", 1)])
    p.produce(topics, key=b"1", value=b"{esto no es JSON", headers=cab)  # misma clave → misma partición
    p.produce(topics, key=b"1", value=json.dumps({"id": 1, "importe": "abc"}).encode(), headers=cab)
    p.flush(10)
    publicar(topics, [(1, "-3.00", 5)])  # detrás de los venenosos, en la misma partición

    parar = en_marcha()
    try:
        assert esperar(lambda: str(filas().get(1)) == "-3.00")  # el último llega: la partición no se atasca
    finally:
        parar()

    c = Consumer(KAFKA | {"group.id": f"lector-{uuid.uuid4()}", "auto.offset.reset": "earliest"})
    c.subscribe([ajustes().topic_dlq])
    aparcados = []
    limite = time.monotonic() + 20
    while len(aparcados) < 2 and time.monotonic() < limite:
        m = c.poll(1)
        if m is not None and not m.error():
            aparcados.append(dict(m.headers()))
    c.close()
    assert [h["error"].decode().split("(")[0] for h in aparcados] == ["JSONDecodeError", "KeyError"]
    assert all(h["origen"].decode().startswith(topics) for h in aparcados)  # topic/partición/offset de origen


# ── Módulo 85, ejercicio 4: reconstruir para recuperar un dato que antes se ignoraba ──
def test_reconstruir_recupera_revisado(topics):
    from sqlalchemy import text, update

    from estadisticas.infrastructure.database.sesiones import motor

    def evento(pk, revisado, version):
        return json.dumps({"id": pk, "hogar_id": 1, "cuenta_id": 1, "fecha": "2026-10-01", "importe": "-1.00",
                           "categoria_id": None, "comercio_id": None, "origen": "extracto",
                           "revisado": revisado}).encode()  # fmt: skip

    from confluent_kafka import Producer

    p = Producer(KAFKA)
    for pk in range(1, 5):
        p.produce(
            topics,
            key=str(pk).encode(),
            value=evento(pk, pk % 2 == 0, pk),
            headers=[("version", str(pk)), ("esquema", "1")],
        )
    p.flush(10)

    def sin_revisar():
        with motor().connect() as c:
            return c.execute(text("SELECT count(*) FROM movimientos WHERE NOT revisado")).scalar()

    parar = en_marcha()
    try:
        assert esperar(lambda: len(filas()) == 4)
    finally:
        parar()
    assert sin_revisar() == 2
    # Así quedaría una proyección que existía ANTES de la migración 0002: todo con el valor por defecto
    with sesion() as s, s.begin():
        s.execute(update(MovimientoModel).values(revisado=True))
    assert sin_revisar() == 0  # mal: los mensajes decían otra cosa

    container.reconstruir_proyeccion().ejecutar()
    parar = en_marcha()
    try:
        assert esperar(lambda: len(filas()) == 4 and sin_revisar() == 2)  # releídos desde el offset 0
    finally:
        parar()


# ── Módulo 85, ejercicio 5: varios consumidores en el mismo grupo ──
def test_dos_consumidores_se_reparten_las_particiones(topics):
    from confluent_kafka.admin import AdminClient

    publicar(topics, [(pk, "-1.00", pk) for pk in range(1, 61)])  # 60 claves: caen en las 3 particiones
    parar_a, parar_b = en_marcha(), en_marcha()
    try:
        assert esperar(lambda: len(filas()) == 60)
        admin = AdminClient(KAFKA)

        def reparto():
            grupo = admin.describe_consumer_groups([ajustes().kafka_grupo])[ajustes().kafka_grupo].result()
            return sorted(
                len([tp for tp in m.assignment.topic_partitions if tp.topic == topics]) for m in grupo.members
            )

        assert esperar(lambda: reparto() == [1, 2])  # 3 particiones entre 2 consumidores: 1 + 2
        parar_b()  # uno se va: el otro se queda con todo (rebalanceo)
        assert esperar(lambda: reparto() == [3])
    finally:
        parar_a()
        parar_b()


# ── Módulo 89, ejercicio 1: reintentar los aparcados ──
def aparcados_en_kafka() -> int:
    from confluent_kafka import Consumer, TopicPartition

    c = Consumer(KAFKA | {"group.id": f"contar-{uuid.uuid4()}"})
    _inicio, fin = c.get_watermark_offsets(TopicPartition(ajustes().topic_dlq, 0), timeout=10)
    c.close()
    return fin


def test_reintentar_los_aparcados(topics, monkeypatch):
    from confluent_kafka import Producer

    from estadisticas.domain.bo.movimiento import Movimiento
    from estadisticas.infrastructure.consumer.reintentos_kafka import reintentar

    original, con_bug = Movimiento.desde_evento.__func__, {"activo": True}

    def desde_evento(cls, pk, datos, version):  # un bug del servicio: el movimiento 2 "no se puede leer"
        if con_bug["activo"] and pk == 2:
            raise ValueError("bug en el servicio")
        return original(cls, pk, datos, version)

    monkeypatch.setattr(Movimiento, "desde_evento", classmethod(desde_evento))
    publicar(topics, [(1, "-1.00", 1), (2, "-2.00", 2), (3, "-3.00", 3)])
    p = Producer(KAFKA)
    p.produce(topics, key=b"4", value=b"{roto", headers=[("version", "4"), ("esquema", "1")])  # este, sin arreglo
    p.flush(10)
    parar = en_marcha()
    try:
        assert esperar(lambda: set(filas()) == {1, 3} and aparcados_en_kafka() == 2)
    finally:
        parar()
    with sesion() as s:
        progreso = s.execute(select(ProgresoModel.particion, ProgresoModel.offset)).all()

    con_bug["activo"] = False  # se despliega el arreglo
    assert reintentar() == 2  # los dos aparcados: el 2 se aplica; el JSON roto se vuelve a aparcar
    assert str(filas()[2]) == "-2.00" and set(filas()) == {1, 2, 3}
    assert aparcados_en_kafka() == 3  # el roto, otra vez al final (y no se relee en la misma pasada)
    with sesion() as s:  # el progreso de las particiones no ha retrocedido
        assert s.execute(select(ProgresoModel.particion, ProgresoModel.offset)).all() == progreso
    assert reintentar() == 1  # la siguiente vez, solo lo nuevo: el grupo de reintentos recuerda dónde se quedó
