# eventos/infrastructure/messaging/instantanea.py — el estado actual de todo, al outbox: para la primera carga o
# para reparar una proyección (módulos 85 y 88)
from eventos.domain.services import mensajes
from eventos.infrastructure.database.models.evento_pendiente_model import EventoPendiente as EventoPendienteModel
from eventos.infrastructure.messaging.outbox_django import fila_del_outbox, traza_en_curso


def instantanea(*, hogar_id: int | None = None, lote: int = 2000) -> int:
    """Un mensaje por cada movimiento y membresía que existe HOY (tipo "instantanea").

    Para la primera puesta en marcha (los datos de antes del módulo 85 no tienen eventos) y para reparar
    una proyección que se ha desviado. Repetirla es inofensivo: el consumidor se queda con la última versión.
    """
    from finanzas.models import Movimiento
    from hogares.models import Membresia

    n = 0
    traza = traza_en_curso()
    movimientos = Movimiento.objects.order_by("pk")
    membresias = Membresia.objects.order_by("pk")
    if hogar_id is not None:
        movimientos = movimientos.filter(hogar_id=hogar_id)
        membresias = membresias.filter(hogar_id=hogar_id)

    pendientes: list[EventoPendienteModel] = [
        fila_del_outbox(mensajes.membresia(mb.hogar_id, mb.usuario_id, mb.rol, tipo="instantanea"), traza)
        for mb in membresias.iterator(chunk_size=lote)
    ]
    for m in movimientos.iterator(chunk_size=lote):  # iterator(): no carga 100.000 movimientos en memoria
        pendientes.append(fila_del_outbox(mensajes.movimiento(m, "instantanea"), traza))
        if len(pendientes) >= lote:
            EventoPendienteModel.objects.bulk_create(pendientes)
            n += len(pendientes)
            pendientes = []
    EventoPendienteModel.objects.bulk_create(pendientes)
    return n + len(pendientes)
