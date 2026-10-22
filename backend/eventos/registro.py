"""Escribir eventos en el outbox (módulo 85).

Todas las funciones escriben en la tabla EventoPendiente y NUNCA hablan con Kafka: así el evento se
guarda en la misma transacción que el cambio. Si el cambio se deshace, el evento también.

Los mensajes llevan el ESTADO COMPLETO del objeto (event-carried state transfer), no solo "algo ha
cambiado": el consumidor no tiene que volver a preguntar a Django, y el topic compactado puede
reconstruir cualquier proyección desde cero.
"""

import logging
from collections.abc import Iterable

from django.conf import settings
from django.db import transaction

from .models import EventoPendiente
from .topics import MEMBRESIAS, MOVIMIENTOS

logger = logging.getLogger(__name__)


class SinTransaccion(RuntimeError):
    """Se ha intentado guardar un evento fuera de transaction.atomic()."""


def _en_transaccion() -> bool:
    """¿Estamos dentro de un transaction.atomic() del CÓDIGO (no del que envuelve cada test)?

    En los tests de pytest-django cada test va dentro de una transacción, así que `in_atomic_block` siempre
    es True y no serviría para detectar una vista sin atomic(). Django marca esas transacciones de los tests
    con `_from_testcase`: si solo hay esas, el código de verdad no ha abierto ninguna.
    """
    conexion = transaction.get_connection()
    return any(not getattr(bloque, "_from_testcase", False) for bloque in conexion.atomic_blocks)


def _exigir_transaccion(tipo: str) -> None:
    if _en_transaccion():
        return
    # Sin atomic(), el cambio YA está confirmado (autocommit) cuando llega aquí: si el proceso muere antes
    # de guardar el evento, el cambio queda sin evento y la proyección no se entera nunca.
    if settings.EVENTOS_EXIGIR_TRANSACCION:  # en desarrollo y en los tests: que falle y se vea
        raise SinTransaccion(f"El evento {tipo} se guarda fuera de transaction.atomic()")
    logger.error("Evento %s guardado fuera de una transacción", tipo)  # en producción: avisar, no romper


def _traceparent() -> str:
    """La traza en curso (módulo 84), para que el consumidor cuelgue de la petición que hizo el cambio."""
    from opentelemetry import propagate

    cabeceras: dict[str, str] = {}
    propagate.inject(cabeceras)  # sin OpenTelemetry activo no escribe nada
    return cabeceras.get("traceparent", "")


def _evento(topic: str, clave: str, tipo: str, valor: dict | None, traceparent: str) -> EventoPendiente:
    return EventoPendiente(topic=topic, clave=clave, tipo=tipo, valor=valor, traceparent=traceparent)


# ── Movimientos ──
def datos_movimiento(m) -> dict:
    """Lo que viaja de un movimiento: lo justo para las estadísticas. Ni concepto ni notas (privacidad).

    `m` puede ser el modelo de Django o la entidad del dominio (módulo 87): los dos tienen estos atributos.
    """
    return {
        "id": m.id,
        "hogar_id": m.hogar_id,
        "cuenta_id": m.cuenta_id,
        "fecha": str(m.fecha),  # date o "2026-10-21"
        "importe": str(m.importe),  # Decimal o Dinero, como texto ("-12.50"): un float perdería céntimos
        "categoria_id": m.categoria_id,
        "comercio_id": m.comercio_id,
        "origen": str(m.origen),
        "revisado": m.revisado,
    }


def movimiento_guardado(m, *, creado: bool) -> None:
    tipo = "movimiento.creado" if creado else "movimiento.actualizado"
    _exigir_transaccion(tipo)
    _evento(MOVIMIENTOS, str(m.id), tipo, datos_movimiento(m), _traceparent()).save()


def movimiento_borrado(pk: int) -> None:
    _exigir_transaccion("movimiento.eliminado")
    _evento(MOVIMIENTOS, str(pk), "movimiento.eliminado", None, _traceparent()).save()


def movimientos_cambiados(ids: Iterable[int], *, tipo: str = "movimiento.actualizado") -> int:
    """Para los cambios EN BLOQUE (bulk_create, update(), delete() de un QuerySet), que no emiten señales.

    Lee el estado actual de esos ids: los que existen van con su estado; los que ya no, como tombstone.
    Llamarla DESPUÉS del cambio y dentro de la misma transacción.
    """
    from finanzas.models import Movimiento

    _exigir_transaccion(tipo)
    ids = set(ids)
    traza = _traceparent()
    existentes = {m.pk: m for m in Movimiento.objects.filter(pk__in=ids)}
    eventos = [
        _evento(MOVIMIENTOS, str(pk), tipo, datos_movimiento(existentes[pk]), traza)
        if pk in existentes
        else _evento(MOVIMIENTOS, str(pk), "movimiento.eliminado", None, traza)
        for pk in sorted(ids)
    ]
    EventoPendiente.objects.bulk_create(eventos, batch_size=1000)
    return len(eventos)


# ── Membresías: quién puede ver las estadísticas de qué hogar ──
def _clave_membresia(hogar_id: int, usuario_id: int) -> str:
    return f"{hogar_id}:{usuario_id}"


def membresia_guardada(mb) -> None:
    _exigir_transaccion("membresia.guardada")
    valor = {"hogar_id": mb.hogar_id, "usuario_id": mb.usuario_id, "rol": mb.rol}
    clave = _clave_membresia(mb.hogar_id, mb.usuario_id)
    _evento(MEMBRESIAS, clave, "membresia.guardada", valor, _traceparent()).save()


def membresia_borrada(hogar_id: int, usuario_id: int) -> None:
    _exigir_transaccion("membresia.eliminada")
    clave = _clave_membresia(hogar_id, usuario_id)
    _evento(MEMBRESIAS, clave, "membresia.eliminada", None, _traceparent()).save()


# ── Instantánea: publicar el estado actual entero ──
def instantanea(*, hogar_id: int | None = None, lote: int = 2000) -> int:
    """Un evento por cada movimiento y membresía que existe HOY (tipo "instantanea").

    Para la primera puesta en marcha (los datos de antes del módulo 85 no tienen eventos) y para reparar
    una proyección que se ha desviado. Repetirla es inofensivo: el consumidor se queda con la última versión.
    """
    from finanzas.models import Movimiento
    from hogares.models import Membresia

    n = 0
    traza = _traceparent()
    movimientos = Movimiento.objects.order_by("pk")
    membresias = Membresia.objects.order_by("pk")
    if hogar_id is not None:
        movimientos = movimientos.filter(hogar_id=hogar_id)
        membresias = membresias.filter(hogar_id=hogar_id)

    pendientes: list[EventoPendiente] = []
    for mb in membresias.iterator(chunk_size=lote):
        valor = {"hogar_id": mb.hogar_id, "usuario_id": mb.usuario_id, "rol": mb.rol}
        pendientes.append(
            _evento(MEMBRESIAS, _clave_membresia(mb.hogar_id, mb.usuario_id), "instantanea", valor, traza)
        )
    for m in movimientos.iterator(chunk_size=lote):  # iterator(): no carga 100.000 movimientos en memoria
        pendientes.append(_evento(MOVIMIENTOS, str(m.pk), "instantanea", datos_movimiento(m), traza))
        if len(pendientes) >= lote:
            EventoPendiente.objects.bulk_create(pendientes)
            n += len(pendientes)
            pendientes = []
    EventoPendiente.objects.bulk_create(pendientes)
    return n + len(pendientes)
