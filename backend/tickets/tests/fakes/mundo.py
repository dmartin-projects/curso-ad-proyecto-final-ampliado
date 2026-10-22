"""Todos los fakes de los tickets y los use cases montados con ellos: lo que hace infrastructure/container.py,
en memoria (módulo 88). Contract tests: tests/infrastructure/database/repositories/ y tests/infrastructure/finanzas/.
"""

from datetime import UTC, date, datetime

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.tests.fakes.auditoria_fake import AuditoriaFake
from core.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from core.tests.fakes.reloj_fake import RelojFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from tickets.application.borrar_ticket_use_case.borrar_ticket_use_case import BorrarTicketUseCase
from tickets.application.confirmar_ticket_use_case.confirmar_ticket_use_case import ConfirmarTicketUseCase
from tickets.application.procesar_ticket_use_case.procesar_ticket_use_case import ProcesarTicketUseCase
from tickets.application.reprocesar_ticket_use_case.reprocesar_ticket_use_case import ReprocesarTicketUseCase
from tickets.application.subir_ticket_use_case.subir_ticket_use_case import SubirTicketUseCase
from tickets.application.terminar_sin_gasto_use_case.terminar_sin_gasto_use_case import TerminarSinGastoUseCase
from tickets.domain.bo.ticket import Ticket
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.tests.fakes.extractor_de_datos_fake import ExtractorDeDatosFake
from tickets.tests.fakes.gastos_fake import GastosFake
from tickets.tests.fakes.lector_de_tickets_fake import LectorDeTicketsFake
from tickets.tests.fakes.ticket_command_repository_fake import TicketCommandRepositoryFake

HOY = date(2026, 10, 15)
AHORA = datetime(2026, 10, 15, 18, 30, tzinfo=UTC)
HOGAR, OTRO_HOGAR = 1, 2


def actor(rol: Rol = Rol.MIEMBRO, usuario_id: int = 7) -> Actor:
    return Actor(usuario_id=usuario_id, rol=rol)


class Mundo:
    def __init__(self, *, respuesta=None, umbral=0.8):
        self.tickets = TicketCommandRepositoryFake()
        self.lector, self.extractor = LectorDeTicketsFake(), ExtractorDeDatosFake(respuesta)
        self.gastos = GastosFake((HOGAR, 10), (OTRO_HOGAR, 20))
        self.auditoria, self.eventos = AuditoriaFake(), PublicadorEventosFake()
        self.uow = UnidadDeTrabajoFake(self.tickets, self.gastos, self.auditoria, self.eventos)
        comun = {"tickets": self.tickets, "eventos": self.eventos, "uow": self.uow}
        self.subir = SubirTicketUseCase(gastos=self.gastos, **comun)
        self.procesar = ProcesarTicketUseCase(
            lector=self.lector,
            extractor=self.extractor,
            gastos=self.gastos,
            reloj=RelojFake(HOY, AHORA),
            umbral_confianza=umbral,
            **comun,
        )
        self.terminar = TerminarSinGastoUseCase(reloj=RelojFake(HOY, AHORA), **comun)
        self.confirmar = ConfirmarTicketUseCase(tickets=self.tickets, gastos=self.gastos, uow=self.uow)
        self.reprocesar = ReprocesarTicketUseCase(gastos=self.gastos, auditoria=self.auditoria, **comun)
        self.borrar = BorrarTicketUseCase(**comun)

    def ticket(self, estado=EstadoTicket.PENDIENTE, hogar_id=HOGAR, **extra) -> Ticket:
        """Un ticket ya subido (sin pasar por SubirTicketUseCase: así cada test prueba UN use case)."""
        t = Ticket(
            hogar_id=hogar_id,
            cuenta_id=10,
            nombre_original="ticket.jpg",
            tipo_archivo="image/jpeg",
            huella_archivo=f"h{len(self.tickets.todos())}",
            subido_por_id=7,
            estado=estado,
            **extra,
        )
        self.tickets.crear(t, b"jpeg")
        return t
