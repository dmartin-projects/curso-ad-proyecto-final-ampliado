"""Módulo 95: el anti-corruption layer hacia tickets: lo leído por la IA, del ticket de ESE hogar."""

from datetime import date
from decimal import Decimal

from django.core.files.base import ContentFile

from asistente.domain.read_models.ticket_leido import TicketLeido
from asistente.infrastructure.tickets.tickets_en_tickets import TicketsEnTickets
from conftest import CuentaFactory
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from tickets.models import Ticket


def test_el_ticket_del_hogar_con_lo_que_leyo_la_ia(casa):
    ana, hogar = casa
    ticket = Ticket.objects.create(
        hogar=hogar,
        cuenta=hogar.cuentas.first(),
        archivo=ContentFile(b"jpg", name="ticket.jpg"),
        nombre_original="ticket.jpg",
        tipo="image/jpeg",
        huella_archivo="a" * 64,
        estado=Ticket.Estado.REVISAR,
        datos_ia={
            "comercio": "Frutería Paqui",
            "fecha": "2026-10-20",
            "total": "8.40",
            "lineas": [{"descripcion": "Manzanas", "cantidad": "2", "precio_unitario": "4.20"}],
        },
    )
    lector = Actor(ana.pk, Rol.LECTOR)

    assert TicketsEnTickets().ticket(lector, hogar.pk, ticket.pk) == TicketLeido(
        ticket.pk, "revisar", "Frutería Paqui", date(2026, 10, 20), Decimal("8.40"), ("2 × Manzanas (4.20 c/u)",), None
    )
    otro = CuentaFactory().hogar
    assert TicketsEnTickets().ticket(lector, otro.pk, ticket.pk) is None  # de otro hogar: no existe
