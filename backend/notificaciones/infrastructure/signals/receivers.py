# notificaciones/infrastructure/signals/receivers.py — lo que pasa en las demás apps (sus signals), convertido en
# avisos para las personas (módulos 15, 76 y 88)
#
# Las demás apps no saben que existen las notificaciones: solo emiten señales. Estos receivers son adapters de
# entrada: eligen el texto y los destinatarios y piden NotificarUseCase; los avisos efímeros (refrescar una
# lista, mover una barra de progreso) van directos al adapter de tiempo real.

from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from core.infrastructure.signals.red_de_seguridad import es_cascada
from core.infrastructure.tasks.agrupar import agrupar
from finanzas.infrastructure.signals.finanzas_signals import movimientos_cambiados, presupuesto_superado
from hogares.infrastructure.signals.hogares_signals import miembros_cambiados
from hogares.models import Membresia
from importaciones.infrastructure.signals.importaciones_signals import (
    importacion_analizada,
    importacion_progreso,
    importacion_terminada,
)
from importaciones.models import Importacion
from informes.infrastructure.signals.informes_signals import informe_generado
from notificaciones.application.notificar_use_case.dtos.notificar_input_dto import NotificarInputDTO
from notificaciones.domain.enums.tipo_notificacion import TipoNotificacion as T
from notificaciones.infrastructure import container
from notificaciones.infrastructure.realtime.tiempo_real import avisar_cambio_de_grupos, emitir_a_hogar
from notificaciones.infrastructure.tasks.emitir_evento_hogar_task import emitir_evento_hogar
from tickets.infrastructure.signals.tickets_signals import ticket_terminado
from tickets.models import Ticket


def notificar(**datos) -> None:
    container.notificar().ejecutar(NotificarInputDTO(**datos))


# ── Tickets ──
TEXTOS_TICKET = {
    Ticket.Estado.PROCESADO: (
        T.TICKET_PROCESADO,
        _("Ticket de %(comercio)s procesado"),
        _("Se ha creado un gasto de %(total)s €."),
    ),
    Ticket.Estado.REVISAR: (
        T.TICKET_REVISAR,
        _("Revisa el ticket de %(comercio)s"),
        _("Hay datos que no se han podido confirmar."),
    ),
    Ticket.Estado.ERROR: (
        T.TICKET_ERROR,
        _("No se ha podido procesar un ticket"),
        _("Puedes reprocesarlo o introducir los datos a mano."),
    ),
}


@receiver(ticket_terminado, dispatch_uid="notif_ticket_terminado")
def al_terminar_ticket(sender, ticket, **kwargs):
    emitir_a_hogar(ticket.hogar_id, "tickets_cambiados", {"id": ticket.pk, "estado": ticket.estado})
    if ticket.subido_por is None or ticket.estado not in TEXTOS_TICKET:
        return
    tipo, titulo, mensaje = TEXTOS_TICKET[ticket.estado]
    notificar(
        usuarios=(ticket.subido_por_id,),
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        contexto={
            "comercio": ticket.datos_ia.get("comercio") or ticket.nombre_original,
            "total": ticket.datos_ia.get("total") or "—",
        },
        hogar_id=ticket.hogar_id,
        enlace=f"/hogares/{ticket.hogar_id}/tickets/{ticket.pk}",
    )


# ── Importaciones ──
def _enlace(imp: Importacion) -> str:
    return f"/hogares/{imp.hogar_id}/importaciones/{imp.pk}"


@receiver(importacion_analizada, dispatch_uid="notif_importacion_analizada")
def al_analizar(sender, importacion, **kwargs):
    emitir_a_hogar(importacion.hogar_id, "importaciones_cambiadas", {"id": importacion.pk})
    if importacion.subido_por:
        notificar(
            usuarios=(importacion.subido_por_id,),
            tipo=T.IMPORTACION_LISTA,
            titulo=_("%(archivo)s está listo para revisar"),
            mensaje=_("%(filas)s movimientos leídos; %(duplicadas)s ya existían."),
            contexto={
                "archivo": importacion.nombre_original,
                "filas": importacion.total_filas,
                "duplicadas": importacion.duplicados,
            },
            hogar_id=importacion.hogar_id,
            enlace=_enlace(importacion),
        )


@receiver(importacion_progreso, dispatch_uid="notif_importacion_progreso")
def al_progresar(sender, importacion, **kwargs):
    # efímero: no se guarda, solo mueve la barra de progreso de quien esté mirando
    emitir_a_hogar(
        importacion.hogar_id, "importacion_progreso", {"id": importacion.pk, "progreso": importacion.progreso}
    )


@receiver(importacion_terminada, dispatch_uid="notif_importacion_terminada")
def al_terminar_importacion(sender, importacion, **kwargs):
    emitir_a_hogar(importacion.hogar_id, "importaciones_cambiadas", {"id": importacion.pk})
    if not importacion.subido_por:
        return
    if importacion.estado == Importacion.Estado.COMPLETADA:
        tipo, titulo = T.IMPORTACION_COMPLETADA, _("Importación de %(archivo)s completada")
        mensaje = _("%(creados)s movimientos nuevos y %(conciliados)s conciliados con gastos que ya tenías.")
    else:
        tipo, titulo, mensaje = T.IMPORTACION_ERROR, _("Error al importar %(archivo)s"), _("%(error)s")
    notificar(
        usuarios=(importacion.subido_por_id,),
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        contexto={
            "archivo": importacion.nombre_original,
            "creados": importacion.creados,
            "conciliados": importacion.conciliados,
            "error": importacion.error,
        },
        hogar_id=importacion.hogar_id,
        enlace=_enlace(importacion),
    )


# ── Presupuestos y movimientos ──
@receiver(presupuesto_superado, dispatch_uid="notif_presupuesto_superado")
def al_superar_presupuesto(sender, presupuesto, **kwargs):
    p = presupuesto
    notificar(
        miembros_de=p.hogar_id,
        tipo=T.PRESUPUESTO_SUPERADO,
        titulo=_("Presupuesto de %(categoria)s superado"),
        mensaje=_("Lleváis %(gastado)s € de %(importe)s € en %(mes)s."),
        contexto={
            "categoria": p.categoria.nombre,
            "gastado": abs(p.gastado),
            "importe": p.importe,
            "mes": f"{p.mes:%m/%Y}",
        },
        hogar_id=p.hogar_id,
        enlace=f"/hogares/{p.hogar_id}/presupuestos?mes={p.mes:%Y-%m}",
        email=True,
    )


@receiver(movimientos_cambiados, dispatch_uid="notif_movimientos_cambiados")
def al_cambiar_movimientos(sender, hogar_id, meses, **kwargs):
    agrupar(f"ws-movimientos:{hogar_id}", 2, emitir_evento_hogar, hogar_id, "movimientos_cambiados")


# ── Membresías: los grupos del socket dependen de ellas ──
@receiver(miembros_cambiados, dispatch_uid="notif_miembros_cambiados")
def al_cambiar_miembros(sender, usuario_id, **kwargs):
    avisar_cambio_de_grupos(usuario_id)  # hogares la envía al confirmar un alta o una baja


@receiver(post_delete, sender=Membresia, dispatch_uid="notif_membresia_borrada")
def al_borrar_membresia(sender, instance, origin=None, **kwargs):
    if es_cascada(instance, origin):  # borrar un hogar se lleva sus membresías sin pasar por ningún use case
        transaction.on_commit(lambda: avisar_cambio_de_grupos(instance.usuario_id))


# ── Informes ──
@receiver(informe_generado, dispatch_uid="notif_informe_generado")
def al_generar_informe(sender, informe, **kwargs):
    notificar(
        miembros_de=informe.hogar_id,
        tipo=T.INFORME_LISTO,
        titulo=_("Informe de %(mes)s disponible"),
        contexto={"mes": f"{informe.mes:%m/%Y}"},
        hogar_id=informe.hogar_id,
        enlace=f"/hogares/{informe.hogar_id}/informes",
    )
