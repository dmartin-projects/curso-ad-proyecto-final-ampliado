# eventos/infrastructure/messaging/outbox_django.py — IOutbox con el ORM (módulos 85 y 88)
#
# Todas las escrituras van a la tabla EventoPendiente y NUNCA hablan con Kafka: así el mensaje se guarda en la misma
# transacción que el cambio. Si el cambio se deshace, el mensaje también. Lo usan los publicadores de las apps
# (finanzas, hogares), que lo reciben de su contenedor; qué viaja en cada mensaje lo dice
# eventos/domain/services/mensajes.py.
import logging
from collections.abc import Iterable

from django.conf import settings
from django.db import transaction

from eventos.application.ports.i_outbox import IOutbox
from eventos.domain.services import mensajes
from eventos.domain.vo.mensaje import Mensaje
from eventos.infrastructure.database.models.evento_pendiente_model import EventoPendiente as EventoPendienteModel
from eventos.infrastructure.messaging.sin_transaccion_exception import SinTransaccionException

logger = logging.getLogger(__name__)


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
        raise SinTransaccionException(f"El evento {tipo} se guarda fuera de transaction.atomic()")
    logger.error("Evento %s guardado fuera de una transacción", tipo)  # en producción: avisar, no romper


def traza_en_curso() -> str:
    """La traza en curso (módulo 84), para que el consumidor cuelgue de la petición que hizo el cambio."""
    from opentelemetry import propagate

    cabeceras: dict[str, str] = {}
    propagate.inject(cabeceras)  # sin OpenTelemetry activo no escribe nada
    return cabeceras.get("traceparent", "")


def fila_del_outbox(m: Mensaje, traceparent: str) -> EventoPendienteModel:
    return EventoPendienteModel(topic=m.topic, clave=m.clave, tipo=m.tipo, valor=m.valor, traceparent=traceparent)


class OutboxDjango(IOutbox):
    def _guardar(self, m: Mensaje) -> None:
        _exigir_transaccion(m.tipo)
        fila_del_outbox(m, traza_en_curso()).save()

    def movimiento_guardado(self, m, *, creado: bool) -> None:
        self._guardar(mensajes.movimiento(m, "movimiento.creado" if creado else "movimiento.actualizado"))

    def movimiento_borrado(self, movimiento_id: int) -> None:
        self._guardar(mensajes.movimiento_eliminado(movimiento_id))

    def movimientos_cambiados(self, ids: Iterable[int], *, tipo: str = "movimiento.actualizado") -> int:
        """Lee el estado ACTUAL de esos ids: llamarla DESPUÉS del cambio y dentro de la misma transacción."""
        from finanzas.models import Movimiento  # lectura entre apps: el estado completo viaja en el mensaje

        _exigir_transaccion(tipo)
        ids = set(ids)
        traza = traza_en_curso()
        existentes = {m.pk: m for m in Movimiento.objects.filter(pk__in=ids)}
        filas = [
            fila_del_outbox(
                mensajes.movimiento(existentes[pk], tipo) if pk in existentes else mensajes.movimiento_eliminado(pk),
                traza,
            )
            for pk in sorted(ids)
        ]
        EventoPendienteModel.objects.bulk_create(filas, batch_size=1000)
        return len(filas)

    def membresia_guardada(self, hogar_id: int, usuario_id: int, rol: str) -> None:
        self._guardar(mensajes.membresia(hogar_id, usuario_id, rol))

    def membresia_borrada(self, hogar_id: int, usuario_id: int) -> None:
        self._guardar(mensajes.membresia_eliminada(hogar_id, usuario_id))
