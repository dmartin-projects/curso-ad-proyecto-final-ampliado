"""Cambios de uno en uno → outbox (módulo 85).

post_save y post_delete se ejecutan DENTRO de la operación que los dispara, así que el evento entra en la
misma transacción que el cambio… siempre que haya una transacción (ver registro._exigir_transaccion).
Los cambios en bloque no emiten señales: esos llaman a registro.movimientos_cambiados() a mano.

Módulo 87: los use cases de finanzas publican sus eventos ellos mismos
(finanzas/infrastructure/messaging/publicador_eventos_django.py) y sus instancias vienen marcadas; estos receivers
quedan para quien aún guarda sin use case (hasta el módulo 88).
"""

from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from core.infrastructure.signals.red_de_seguridad import lo_publica_un_caso_de_uso
from finanzas.models import Categoria, Movimiento
from hogares.models import Membresia

from . import registro


@receiver(post_save, sender=Movimiento, dispatch_uid="eventos_movimiento_guardado")
def al_guardar_movimiento(sender, instance, created, raw=False, **kwargs):
    if raw or lo_publica_un_caso_de_uso(instance):  # loaddata, o ya lo ha publicado el use case
        return
    registro.movimiento_guardado(instance, creado=created)


@receiver(post_delete, sender=Movimiento, dispatch_uid="eventos_movimiento_borrado")
def al_borrar_movimiento(sender, instance, **kwargs):
    # También al borrar un hogar o una cuenta: el borrado en cascada emite post_delete por cada movimiento
    if not lo_publica_un_caso_de_uso(instance):
        registro.movimiento_borrado(instance.pk)


@receiver(post_save, sender=Membresia, dispatch_uid="eventos_membresia_guardada")
def al_guardar_membresia(sender, instance, raw=False, **kwargs):
    if not raw:
        registro.membresia_guardada(instance)


@receiver(post_delete, sender=Membresia, dispatch_uid="eventos_membresia_borrada")
def al_borrar_membresia(sender, instance, **kwargs):
    registro.membresia_borrada(instance.hogar_id, instance.usuario_id)


# Borrar una categoría deja sus movimientos con categoria=NULL (on_delete=SET_NULL)… con un UPDATE en bloque
# que NO emite post_save. finanzas/signals.py ya lo resuelve para el dashboard y los presupuestos (módulo 76,
# con los meses afectados); aquí, al lado y con la misma técnica, para Kafka: sin esto, las estadísticas
# seguirían contando esos gastos en una categoría que ya no existe. pre_delete apunta qué movimientos tenía
# (después del UPDATE ya no se pueden encontrar) y post_delete, con el UPDATE hecho, publica su nuevo estado.
# Las subcategorías (CASCADE) pasan por aquí también.
@receiver(pre_delete, sender=Categoria, dispatch_uid="eventos_categoria_va_a_borrarse")
def antes_de_borrar_categoria(sender, instance, **kwargs):
    instance._movimientos_afectados = list(instance.movimientos.values_list("pk", flat=True))


@receiver(post_delete, sender=Categoria, dispatch_uid="eventos_categoria_borrada")
def al_borrar_categoria(sender, instance, **kwargs):
    if ids := getattr(instance, "_movimientos_afectados", None):
        registro.movimientos_cambiados(ids)
