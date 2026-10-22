# tickets/tests/fakes/ticket_command_repository_fake.py — ITicketCommandRepository en memoria (módulo 88)
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia
from tickets.domain.enums.estado_ticket import SIN_TERMINAR, EstadoTicket
from tickets.domain.exceptions.ticket_no_encontrado_exception import TicketNoEncontradoException
from tickets.domain.exceptions.ticket_repetido_exception import TicketRepetidoException
from tickets.domain.repositories.i_ticket_command_repository import ITicketCommandRepository


class TicketCommandRepositoryFake(AlmacenEnMemoria, ITicketCommandRepository):
    def __init__(self):
        super().__init__()
        self.archivos: dict[str, bytes] = {}

    def crear(self, ticket, contenido):
        if any(
            (t.hogar_id, t.huella_archivo) == (ticket.hogar_id, ticket.huella_archivo) for t in self._datos.values()
        ):
            raise TicketRepetidoException()
        self._asignar_id(ticket)
        ticket.archivo = f"tickets/{ticket.hogar_id}/{ticket.id}.jpg"
        self.archivos[ticket.archivo] = contenido
        self._datos[ticket.id] = copia(ticket)

    def obtener(self, hogar_id, ticket_id, *, bloquear=False):
        t = self._datos.get(ticket_id)
        if t is None or t.hogar_id != hogar_id:
            raise TicketNoEncontradoException()
        return copia(t)

    def bloquear(self, ticket_id):
        if ticket_id not in self._datos:
            raise TicketNoEncontradoException()
        return copia(self._datos[ticket_id])

    def reclamar(self, ticket_id):
        t = self._datos.get(ticket_id)
        if t is None or t.estado not in SIN_TERMINAR:
            return None
        t.estado, t.intentos, t.error = EstadoTicket.PROCESANDO, t.intentos + 1, ""
        return copia(t)

    def guardar(self, ticket):
        self._datos[ticket.id] = copia(ticket)

    def guardar_texto(self, ticket_id, texto):
        self._datos[ticket_id].texto_ocr = texto

    def terminar_sin_gasto(self, ticket_id, estado, mensaje, ahora):
        t = self._datos[ticket_id]
        if t.estado not in SIN_TERMINAR:
            return False
        t.estado, t.error, t.procesado_en = estado, mensaje, ahora
        return True

    def leer_archivo(self, ticket):
        return self.archivos[ticket.archivo]

    def eliminar(self, ticket):
        self._datos.pop(ticket.id, None)
