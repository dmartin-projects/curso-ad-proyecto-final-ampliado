# tickets/infrastructure/container.py — composition root de los tickets (módulo 88)
from django.conf import settings

from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.auditoria_django import AuditoriaDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from tickets.application.borrar_ticket_use_case.borrar_ticket_use_case import BorrarTicketUseCase
from tickets.application.borrar_ticket_use_case.i_borrar_ticket_use_case import IBorrarTicketUseCase
from tickets.application.confirmar_ticket_use_case.confirmar_ticket_use_case import ConfirmarTicketUseCase
from tickets.application.confirmar_ticket_use_case.i_confirmar_ticket_use_case import IConfirmarTicketUseCase
from tickets.application.contar_tickets_atascados_use_case.contar_tickets_atascados_use_case import (
    ContarTicketsAtascadosUseCase,
)
from tickets.application.contar_tickets_atascados_use_case.i_contar_tickets_atascados_use_case import (
    IContarTicketsAtascadosUseCase,
)
from tickets.application.listar_tickets_use_case.i_listar_tickets_use_case import IListarTicketsUseCase
from tickets.application.listar_tickets_use_case.listar_tickets_use_case import ListarTicketsUseCase
from tickets.application.obtener_ticket_use_case.i_obtener_ticket_use_case import IObtenerTicketUseCase
from tickets.application.obtener_ticket_use_case.obtener_ticket_use_case import ObtenerTicketUseCase
from tickets.application.procesar_ticket_use_case.i_procesar_ticket_use_case import IProcesarTicketUseCase
from tickets.application.procesar_ticket_use_case.procesar_ticket_use_case import ProcesarTicketUseCase
from tickets.application.reprocesar_ticket_use_case.i_reprocesar_ticket_use_case import IReprocesarTicketUseCase
from tickets.application.reprocesar_ticket_use_case.reprocesar_ticket_use_case import ReprocesarTicketUseCase
from tickets.application.subir_ticket_use_case.i_subir_ticket_use_case import ISubirTicketUseCase
from tickets.application.subir_ticket_use_case.subir_ticket_use_case import SubirTicketUseCase
from tickets.application.terminar_sin_gasto_use_case.i_terminar_sin_gasto_use_case import ITerminarSinGastoUseCase
from tickets.application.terminar_sin_gasto_use_case.terminar_sin_gasto_use_case import TerminarSinGastoUseCase
from tickets.infrastructure.database.repositories.ticket_command_repository_orm import TicketCommandRepositoryORM
from tickets.infrastructure.database.repositories.ticket_query_service_orm import TicketQueryServiceORM
from tickets.infrastructure.finanzas.gastos_en_finanzas import GastosEnFinanzas
from tickets.infrastructure.ia.extractor_ia import ExtractorIA
from tickets.infrastructure.messaging.publicador_eventos_django import PublicadorEventosDjango
from tickets.infrastructure.ocr.lector_tesseract import LectorTesseract


def _transaccion_y_eventos() -> dict:
    return {"uow": UnidadDeTrabajoDjango(), "eventos": PublicadorEventosDjango()}


def subir_ticket() -> ISubirTicketUseCase:
    return SubirTicketUseCase(
        tickets=TicketCommandRepositoryORM(), gastos=GastosEnFinanzas(), **_transaccion_y_eventos()
    )


def procesar_ticket() -> IProcesarTicketUseCase:
    return ProcesarTicketUseCase(
        tickets=TicketCommandRepositoryORM(),
        lector=LectorTesseract(),
        extractor=ExtractorIA(),
        gastos=GastosEnFinanzas(),
        reloj=RelojDjango(),
        umbral_confianza=settings.TICKETS_UMBRAL_CONFIANZA,  # se lee en cada llamada: override_settings funciona
        **_transaccion_y_eventos(),
    )


def terminar_sin_gasto() -> ITerminarSinGastoUseCase:
    return TerminarSinGastoUseCase(
        tickets=TicketCommandRepositoryORM(), reloj=RelojDjango(), **_transaccion_y_eventos()
    )


def confirmar_ticket() -> IConfirmarTicketUseCase:
    return ConfirmarTicketUseCase(
        tickets=TicketCommandRepositoryORM(), gastos=GastosEnFinanzas(), uow=UnidadDeTrabajoDjango()
    )


def reprocesar_ticket() -> IReprocesarTicketUseCase:
    return ReprocesarTicketUseCase(
        tickets=TicketCommandRepositoryORM(),
        gastos=GastosEnFinanzas(),
        auditoria=AuditoriaDjango(),
        **_transaccion_y_eventos(),
    )


def borrar_ticket() -> IBorrarTicketUseCase:
    return BorrarTicketUseCase(tickets=TicketCommandRepositoryORM(), **_transaccion_y_eventos())


# ── Lectura ──
def listar_tickets() -> IListarTicketsUseCase:
    return ListarTicketsUseCase(tickets=TicketQueryServiceORM())


def obtener_ticket() -> IObtenerTicketUseCase:
    return ObtenerTicketUseCase(tickets=TicketQueryServiceORM())


def contar_tickets_atascados() -> IContarTicketsAtascadosUseCase:
    return ContarTicketsAtascadosUseCase(tickets=TicketQueryServiceORM())
