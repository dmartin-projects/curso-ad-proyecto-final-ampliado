# tickets/application/procesar_ticket_use_case/procesar_ticket_use_case.py (módulos 74 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.vo.actor import Actor
from tickets.application.ports.i_extractor_de_datos import IExtractorDeDatos
from tickets.application.ports.i_gastos import IGastos
from tickets.application.ports.i_lector_de_tickets import ILectorDeTickets
from tickets.application.procesar_ticket_use_case.dtos.procesar_ticket_input_dto import ProcesarTicketInputDTO
from tickets.application.procesar_ticket_use_case.i_procesar_ticket_use_case import IProcesarTicketUseCase
from tickets.domain.bo.ticket import Ticket
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.events.ticket_terminado_event import TicketTerminadoEvent
from tickets.domain.exceptions.datos_ilegibles_exception import DatosIlegiblesException
from tickets.domain.repositories.i_ticket_command_repository import ITicketCommandRepository
from tickets.domain.services.motivos_de_revision import motivos_de_revision


class ProcesarTicketUseCase(IProcesarTicketUseCase):
    """OCR → IA → gasto. Idempotente: una entrega duplicada de la tarea no crea otro gasto.

    Las dos llamadas lentas (OCR e IA) van FUERA de la transacción: no se tiene una fila bloqueada durante segundos.
    La transacción empieza al aplicar el resultado, con el ticket bloqueado: si otro worker se adelantó, no se hace
    nada. Los errores pasajeros del extractor se propagan: la tarea reintenta (módulo 74). Lo pide una tarea, sin
    persona: no exige rol.
    """

    def __init__(
        self,
        *,
        tickets: ITicketCommandRepository,
        lector: ILectorDeTickets,
        extractor: IExtractorDeDatos,
        gastos: IGastos,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
        reloj: IReloj,
        umbral_confianza: float,
    ):
        self.tickets, self.lector, self.extractor, self.gastos = tickets, lector, extractor, gastos
        self.eventos, self.uow, self.reloj, self.umbral = eventos, uow, reloj, umbral_confianza

    def _leer(self, ticket: Ticket) -> tuple[str, bytes | None]:
        """El texto (el de un intento anterior, si sirvió) y la imagen solo si el OCR no ha leído nada útil."""
        if ticket.texto_reutilizable:
            return ticket.texto_ocr, None
        lectura = self.lector.leer(self.tickets.leer_archivo(ticket), ticket.tipo_archivo)
        self.tickets.guardar_texto(ticket.id, lectura.texto)
        return lectura.texto, None if lectura.es_util else lectura.imagen_png

    def ejecutar(self, entrada: ProcesarTicketInputDTO) -> EstadoTicket | None:
        """El estado en el que queda, o None si no había nada que hacer."""
        ticket_id = entrada.ticket_id
        ticket = self.tickets.reclamar(ticket_id)
        if ticket is None:
            return None
        texto, imagen = self._leer(ticket)
        try:
            datos = self.extractor.extraer(texto, self.gastos.nombres_de_categorias(ticket.hogar_id), imagen)
        except DatosIlegiblesException as e:  # reintentar no lo arreglará: que lo complete la persona
            with self.uow:
                if self.tickets.terminar_sin_gasto(
                    ticket_id, EstadoTicket.REVISAR, str(e.mensaje)[:1000], self.reloj.ahora()
                ):
                    self.eventos.publicar(TicketTerminadoEvent(ticket_id))
            return EstadoTicket.REVISAR
        with self.uow:
            ticket = self.tickets.bloquear(ticket_id)
            if ticket.estado != EstadoTicket.PROCESANDO:
                return ticket.estado  # otro worker ya lo terminó
            motivos = motivos_de_revision(datos, hoy=self.reloj.hoy(), umbral=self.umbral)
            gasto = None
            if datos.total is not None:  # sin total no hay gasto: lo completará la persona al confirmar
                gasto = self.gastos.apuntar(
                    hogar_id=ticket.hogar_id,
                    actor=Actor.sistema(en_nombre_de=ticket.subido_por_id),  # el gasto, a nombre de quien lo subió
                    cuenta_id=ticket.cuenta_id,
                    fecha=datos.fecha or self.reloj.hoy(),
                    total=datos.total,
                    concepto=datos.comercio or "Ticket",
                    comercio=datos.comercio,
                    nif=datos.nif,
                    categoria_sugerida=datos.categoria,
                    revisado=not motivos,
                )
            ticket.aplicar(datos, motivos, gasto, self.reloj.ahora())
            self.tickets.guardar(ticket)
            self.eventos.publicar(TicketTerminadoEvent(ticket.id))
        return ticket.estado
