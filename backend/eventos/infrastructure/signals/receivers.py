# eventos/infrastructure/signals/receivers.py — lo que cambia en la base de datos sin pasar por un use case: las cascadas → outbox (módulos 85 y 88)
#
# Las altas, cambios y bajas los publican los use cases (finanzas y hogares, con su publicador y el port IOutbox).
# Aquí solo quedan los efectos de la propia base de datos: borrar un hogar se lleva sus movimientos y membresías
# (CASCADE) y borrar una categoría deja sus movimientos sin categoría (SET_NULL, un UPDATE sin señales).
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

from core.infrastructure.signals.red_de_seguridad import es_cascada
from eventos.infrastructure.messaging.outbox_django import OutboxDjango
from finanzas.models import Categoria, Movimiento
from hogares.models import Membresia

_outbox = OutboxDjango()


@receiver(post_delete, sender=Movimiento, dispatch_uid="eventos_movimiento_borrado")
def al_borrar_movimiento(sender, instance, origin=None, **kwargs):
    # Borrar un hogar se lleva sus movimientos (CASCADE) sin pasar por ningún use case: su tombstone, aquí.
    # Lo que borra un use case lo publica él (finanzas/infrastructure/messaging/publicador_eventos_django.py).
    if es_cascada(instance, origin):
        _outbox.movimiento_borrado(instance.pk)


@receiver(post_delete, sender=Membresia, dispatch_uid="eventos_membresia_borrada")
def al_borrar_membresia(sender, instance, origin=None, **kwargs):
    # Las altas, los cambios de rol y las bajas los publica el use case (hogares/infrastructure/messaging/). Aquí solo
    # las cascadas: borrar un hogar se lleva sus membresías sin pasar por ningún use case
    if es_cascada(instance, origin):
        _outbox.membresia_borrada(instance.hogar_id, instance.usuario_id)


# Borrar una categoría deja sus movimientos con categoria=NULL (on_delete=SET_NULL)… con un UPDATE en bloque
# que NO emite post_save. finanzas/infrastructure/signals/receivers.py lo resuelve para el dashboard y los
# presupuestos (con los meses afectados); aquí, al lado y con la misma técnica, para Kafka: sin esto, las
# estadísticas seguirían contando esos gastos en una categoría que ya no existe. pre_delete apunta qué movimientos
# tenía (después del UPDATE ya no se pueden encontrar) y post_delete, con el UPDATE hecho, publica su nuevo estado.
# Las subcategorías (CASCADE) pasan por aquí también.
@receiver(pre_delete, sender=Categoria, dispatch_uid="eventos_categoria_va_a_borrarse")
def antes_de_borrar_categoria(sender, instance, **kwargs):
    instance._movimientos_afectados = list(instance.movimientos.values_list("pk", flat=True))


@receiver(post_delete, sender=Categoria, dispatch_uid="eventos_categoria_borrada")
def al_borrar_categoria(sender, instance, **kwargs):
    if ids := getattr(instance, "_movimientos_afectados", None):
        _outbox.movimientos_cambiados(ids)
