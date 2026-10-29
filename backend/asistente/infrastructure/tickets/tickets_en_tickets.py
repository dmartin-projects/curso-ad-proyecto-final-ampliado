# asistente/infrastructure/tickets/tickets_en_tickets.py — ITickets con el use case de consulta de tickets (módulo 95)
from datetime import date
from decimal import Decimal

from asistente.application.ports.i_tickets import ITickets
from asistente.domain.read_models.ticket_leido import TicketLeido
from tickets.application.obtener_ticket_use_case.dtos.obtener_ticket_input_dto import ObtenerTicketInputDTO
from tickets.infrastructure import container as tickets


class TicketsEnTickets(ITickets):
    def ticket(self, actor, hogar_id, ticket_id):
        t = tickets.obtener_ticket().ejecutar(ObtenerTicketInputDTO(hogar_id, actor, ticket_id))
        if t is None:
            return None
        datos = t.datos_ia or {}  # lo que leyó la IA (en JSON: fechas e importes como texto)
        lineas = datos.get("lineas") or []
        return TicketLeido(
            id=t.id,
            estado=t.estado,
            comercio=datos.get("comercio") or "",
            fecha=date.fromisoformat(datos["fecha"]) if datos.get("fecha") else None,
            total=Decimal(str(datos["total"])) if datos.get("total") is not None else None,
            lineas=tuple(f"{li['cantidad']} × {li['descripcion']} ({li['precio_unitario']} c/u)" for li in lineas),
            gasto_id=t.gasto.id if t.gasto else None,
        )
