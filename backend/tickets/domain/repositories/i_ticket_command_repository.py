# tickets/domain/repositories/i_ticket_command_repository.py — el lado de escritura de los tickets (módulo 88)
from abc import ABC, abstractmethod
from datetime import datetime

from tickets.domain.bo.ticket import Ticket
from tickets.domain.enums.estado_ticket import EstadoTicket


class ITicketCommandRepository(ABC):
    @abstractmethod
    def crear(self, ticket: Ticket, contenido: object) -> None:
        """Guarda el ticket y su archivo (`contenido`: el file-like que da el adapter de entrada). Le pone el id
        y el nombre del archivo. El mismo archivo dos veces en el hogar: TicketRepetidoException."""

    @abstractmethod
    def obtener(self, hogar_id: int, ticket_id: int, *, bloquear: bool = False) -> Ticket:
        """De ESE hogar, o TicketNoEncontradoException. `bloquear`: nadie más lo cambia hasta el final de la
        transacción."""

    @abstractmethod
    def bloquear(self, ticket_id: int) -> Ticket:
        """Para los procesos (no hay hogar que comprobar: el id viene de una tarea, no de fuera)."""

    @abstractmethod
    def reclamar(self, ticket_id: int) -> Ticket | None:
        """pendiente/procesando → procesando, un intento más, en una operación atómica. None si ya no hay nada
        que hacer (otra entrega de la misma tarea ya lo terminó)."""

    @abstractmethod
    def guardar(self, ticket: Ticket) -> None:
        """Actualiza el ticket y sus líneas."""

    @abstractmethod
    def guardar_texto(self, ticket_id: int, texto: str) -> None:
        """El texto del OCR, en cuanto se tiene: si la IA falla, el reintento no repite el OCR."""

    @abstractmethod
    def terminar_sin_gasto(self, ticket_id: int, estado: EstadoTicket, mensaje: str, ahora: datetime) -> bool:
        """Error o revisión a mano, SOLO si aún estaba sin terminar (UPDATE condicional). True si lo ha cambiado."""

    @abstractmethod
    def leer_archivo(self, ticket: Ticket) -> bytes: ...

    @abstractmethod
    def eliminar(self, ticket: Ticket) -> None: ...
