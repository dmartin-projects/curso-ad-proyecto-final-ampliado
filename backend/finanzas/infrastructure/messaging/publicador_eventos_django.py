# finanzas/infrastructure/messaging/publicador_eventos_django.py — IPublicadorEventos con Django
# (módulos 76, 77, 85, 87 y 88)
#
# Traduce cada evento de dominio a lo que significa en ESTE sistema:
#   - un mensaje en el outbox (el port IOutbox de eventos), en la misma transacción que el cambio → Kafka (85);
#   - un aviso interno (finanzas_signals.py) cuando la transacción se confirme → dashboard, presupuestos y WebSocket.
from django.db import transaction

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from eventos.application.ports.i_outbox import IOutbox
from finanzas.domain.events.categorias_cambiadas_event import CategoriasCambiadasEvent
from finanzas.domain.events.movimiento_eliminado_event import MovimientoEliminadoEvent
from finanzas.domain.events.movimiento_modificado_event import MovimientoModificadoEvent
from finanzas.domain.events.movimiento_registrado_event import MovimientoRegistradoEvent
from finanzas.domain.events.movimientos_apuntados_event import MovimientosApuntadosEvent
from finanzas.domain.events.movimientos_eliminados_event import MovimientosEliminadosEvent
from finanzas.domain.events.movimientos_recategorizados_event import MovimientosRecategorizadosEvent
from finanzas.domain.events.presupuesto_superado_event import PresupuestoSuperadoEvent
from finanzas.domain.events.presupuestos_cambiados_event import PresupuestosCambiadosEvent
from finanzas.infrastructure.cache import dashboard_cache
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel
from finanzas.infrastructure.database.models.presupuesto_model import Presupuesto as PresupuestoModel
from finanzas.infrastructure.signals import finanzas_signals


def _al_confirmar_movimientos_cambiados(sender, hogar_id: int, meses) -> None:
    fechas = {mes.inicio for mes in meses}  # los receptores esperan date (día 1), como siempre
    transaction.on_commit(
        lambda: finanzas_signals.movimientos_cambiados.send(sender=sender, hogar_id=hogar_id, meses=fechas)
    )


def _avisar_presupuesto_superado(presupuesto_id: int, gastado) -> None:
    presupuesto = PresupuestoModel.objects.select_related("categoria", "hogar").get(pk=presupuesto_id)
    presupuesto.gastado = gastado.cantidad
    finanzas_signals.presupuesto_superado.send(sender=PresupuestoModel, presupuesto=presupuesto)


class PublicadorEventosDjango(IPublicadorEventos):
    def __init__(self, *, outbox: IOutbox):
        # El outbox es un port del publicador (módulo 88): se lo da el contenedor, y en un test se puede cambiar
        # por uno que falle sin tocar nada más.
        self.outbox = outbox

    def publicar(self, *eventos: object) -> None:
        registro = self.outbox
        for evento in eventos:
            match evento:
                case MovimientoRegistradoEvent(movimiento=m):
                    registro.movimiento_guardado(m, creado=True)
                    _al_confirmar_movimientos_cambiados(MovimientoModel, m.hogar_id, {m.mes})
                case MovimientoModificadoEvent(movimiento=m, meses=meses):
                    registro.movimiento_guardado(m, creado=False)
                    _al_confirmar_movimientos_cambiados(MovimientoModel, m.hogar_id, meses)
                case MovimientoEliminadoEvent(movimiento_id=pk, hogar_id=hogar_id, mes=mes):
                    registro.movimiento_borrado(pk)
                    _al_confirmar_movimientos_cambiados(MovimientoModel, hogar_id, {mes})
                case MovimientosRecategorizadosEvent(hogar_id=hogar_id, ids=ids, meses=meses):
                    registro.movimientos_cambiados(ids)  # lee su estado ya actualizado, en esta transacción
                    _al_confirmar_movimientos_cambiados(MovimientoModel, hogar_id, meses)
                case MovimientosApuntadosEvent(hogar_id=hogar_id, ids=ids, meses=meses):  # módulo 88
                    registro.movimientos_cambiados(ids, tipo="movimiento.creado")
                    _al_confirmar_movimientos_cambiados(MovimientoModel, hogar_id, meses)
                case MovimientosEliminadosEvent(hogar_id=hogar_id, ids=ids, meses=meses):  # módulo 88
                    registro.movimientos_cambiados(ids)  # ya no existen: un tombstone por cada uno
                    _al_confirmar_movimientos_cambiados(MovimientoModel, hogar_id, meses)
                case CategoriasCambiadasEvent(hogar_id=hogar_id):
                    transaction.on_commit(lambda hogar_id=hogar_id: dashboard_cache.invalidar(hogar_id))
                case PresupuestosCambiadosEvent(hogar_id=hogar_id, meses=meses):
                    _al_confirmar_movimientos_cambiados(PresupuestoModel, hogar_id, meses)  # comprobar esos meses
                case PresupuestoSuperadoEvent(presupuesto_id=pk, gastado=gastado):
                    transaction.on_commit(lambda pk=pk, gastado=gastado: _avisar_presupuesto_superado(pk, gastado))
                case _:
                    raise TypeError(f"Evento sin traducción: {evento!r}")  # mejor que perderlo en silencio
