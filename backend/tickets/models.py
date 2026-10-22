# tickets/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models). Viven en
# infrastructure/database/models/, uno por archivo; este módulo es la puerta de entrada (módulos 87 y 88).
# ruta_ticket también: la migración 0001 la usa como tickets.models.ruta_ticket.
from tickets.infrastructure.database.models.linea_ticket_model import LineaTicket
from tickets.infrastructure.database.models.ticket_model import Ticket, ruta_ticket

__all__ = ["LineaTicket", "Ticket", "ruta_ticket"]
