# finanzas/infrastructure/signals/receivers.py — adapters de entrada que reaccionan a signals (módulos 15, 76, 77, 87 y 88)
from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from core.infrastructure.signals.red_de_seguridad import vigilar
from core.infrastructure.tasks.agrupar import agrupar
from finanzas.application.crear_categorias_por_defecto_use_case.dtos.crear_categorias_por_defecto_input_dto import (
    CrearCategoriasPorDefectoInputDTO,
)
from finanzas.infrastructure import container
from finanzas.infrastructure.cache import dashboard_cache
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel
from finanzas.infrastructure.database.models.presupuesto_model import Presupuesto as PresupuestoModel
from finanzas.infrastructure.signals.finanzas_signals import movimientos_cambiados
from finanzas.infrastructure.tasks.comprobar_presupuestos_task import comprobar_presupuestos_tarea
from hogares.infrastructure.signals.hogares_signals import hogar_creado


@receiver(hogar_creado, dispatch_uid="finanzas_categorias_por_defecto")
def al_crear_hogar(sender, hogar_id, **kwargs):
    container.crear_categorias_por_defecto().ejecutar(CrearCategoriasPorDefectoInputDTO(hogar_id))


@receiver(movimientos_cambiados, dispatch_uid="finanzas_comprobar_presupuestos")
def revisar_presupuestos(sender, hogar_id, meses, **kwargs):
    for mes in meses:
        agrupar(f"presupuestos:{hogar_id}:{mes:%Y-%m}", 10, comprobar_presupuestos_tarea, hogar_id, [mes.isoformat()])


@receiver(movimientos_cambiados, dispatch_uid="finanzas_invalidar_dashboard")
def invalidar_dashboard(sender, hogar_id, **kwargs):
    dashboard_cache.invalidar(hogar_id)  # O(1): sube la versión del hogar (módulo 77)


# Borrar una categoría deja sus movimientos sin categoría (on_delete=SET_NULL) con un UPDATE en bloque, sin
# post_save: pre_delete apunta sus meses (después del UPDATE ya no se sabe qué movimientos eran suyos) y
# post_delete avisa. Las subcategorías, borradas en cascada, pasan también por aquí. No es una escritura sin use
# case: el SET_NULL lo hace la base de datos cuando EliminarCategoriaUseCase borra, igual que los eventos de Kafka
# de esos movimientos (eventos/infrastructure/signals/receivers.py).
@receiver(pre_delete, sender=CategoriaModel, dispatch_uid="finanzas_categoria_va_a_borrarse")
def antes_de_borrar_categoria(sender, instance, **kwargs):
    instance._meses_afectados = set(instance.movimientos.dates("fecha", "month"))


@receiver(post_delete, sender=CategoriaModel, dispatch_uid="finanzas_categoria_borrada")
def al_borrar_categoria(sender, instance, **kwargs):
    if meses := getattr(instance, "_meses_afectados", None):
        hogar_id = instance.hogar_id
        transaction.on_commit(lambda: movimientos_cambiados.send(sender=CategoriaModel, hogar_id=hogar_id, meses=meses))


# ── La alarma (módulo 88): lo que tiene eventos solo se escribe con un use case ──
# Tickets, importaciones y el backoffice piden los use cases de finanzas; una escritura con el ORM perdería sus
# eventos, así que estos receivers no publican nada: avisan (core/infrastructure/signals/red_de_seguridad.py).
@receiver([post_save, post_delete], sender=MovimientoModel, dispatch_uid="finanzas_vigilar_movimientos")
@receiver([post_save, post_delete], sender=PresupuestoModel, dispatch_uid="finanzas_vigilar_presupuestos")
@receiver([post_save, post_delete], sender=CategoriaModel, dispatch_uid="finanzas_vigilar_categorias")
def vigilar_escrituras(sender, instance, origin=None, raw=False, **kwargs):
    vigilar(instance, origin=origin, raw=raw)
