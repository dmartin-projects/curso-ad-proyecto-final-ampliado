# tickets/infrastructure/database/repositories/ticket_command_repository_orm.py — ITicketCommandRepository con el ORM (módulo 88)
from django.db import IntegrityError, transaction
from django.db.models import F

from core.infrastructure.database.guardado import nombre_constraint
from tickets.domain.bo.ticket import Ticket
from tickets.domain.enums.estado_ticket import SIN_TERMINAR, EstadoTicket
from tickets.domain.exceptions.ticket_no_encontrado_exception import TicketNoEncontradoException
from tickets.domain.exceptions.ticket_repetido_exception import TicketRepetidoException
from tickets.domain.repositories.i_ticket_command_repository import ITicketCommandRepository
from tickets.infrastructure.database.mappers.ticket_mapper import datos_a_json, ticket_a_bo
from tickets.infrastructure.database.models.linea_ticket_model import LineaTicket as LineaTicketModel
from tickets.infrastructure.database.models.ticket_model import Ticket as TicketModel

CAMPOS = ["estado", "intentos", "texto_ocr", "datos_ia", "confianza", "error", "procesado_en", "movimiento"]


class TicketCommandRepositoryORM(ITicketCommandRepository):
    def crear(self, ticket: Ticket, contenido) -> None:
        fila = TicketModel(
            hogar_id=ticket.hogar_id,
            cuenta_id=ticket.cuenta_id,
            subido_por_id=ticket.subido_por_id,
            archivo=contenido,  # FileField: al guardar, el storage le da su nombre (ruta_ticket)
            nombre_original=ticket.nombre_original,
            tipo=ticket.tipo_archivo,
            huella_archivo=ticket.huella_archivo,
        )
        try:
            with transaction.atomic():  # savepoint: el error del dominio no rompe la transacción del use case
                fila.save(force_insert=True)
        except IntegrityError as e:
            if nombre_constraint(e) == "ticket_archivo_unico_por_hogar":
                raise TicketRepetidoException() from e
            raise
        ticket.id, ticket.archivo = fila.pk, fila.archivo.name

    def _fila(self, consulta, bloquear: bool) -> TicketModel:
        if bloquear:
            consulta = consulta.select_for_update()
        fila = consulta.first()
        if fila is None:
            raise TicketNoEncontradoException()
        return fila

    def obtener(self, hogar_id: int, ticket_id: int, *, bloquear: bool = False) -> Ticket:
        fila = self._fila(TicketModel.objects.filter(hogar_id=hogar_id, pk=ticket_id), bloquear)
        return ticket_a_bo(fila, list(fila.lineas.all()))

    def bloquear(self, ticket_id: int) -> Ticket:
        fila = self._fila(TicketModel.objects.filter(pk=ticket_id), bloquear=True)
        return ticket_a_bo(fila, list(fila.lineas.all()))

    def reclamar(self, ticket_id: int) -> Ticket | None:
        # Se admite `procesando` para que los reintentos de la tarea puedan continuar (módulo 74)
        reclamado = TicketModel.objects.filter(pk=ticket_id, estado__in=SIN_TERMINAR).update(
            estado=EstadoTicket.PROCESANDO, intentos=F("intentos") + 1, error=""
        )
        return ticket_a_bo(TicketModel.objects.get(pk=ticket_id)) if reclamado else None

    def guardar(self, ticket: Ticket) -> None:
        fila = TicketModel.objects.get(pk=ticket.id)
        fila.estado, fila.intentos, fila.texto_ocr = ticket.estado, ticket.intentos, ticket.texto_ocr
        fila.datos_ia, fila.confianza, fila.error = datos_a_json(ticket.datos), ticket.confianza, ticket.error
        fila.procesado_en, fila.movimiento_id = ticket.procesado_en, ticket.movimiento_id
        fila.save(update_fields=[*CAMPOS, "actualizado"])
        actuales = [(li.descripcion, li.cantidad, li.precio_unitario) for li in fila.lineas.all()]
        if actuales != [(li.descripcion, li.cantidad, li.precio_unitario) for li in ticket.lineas]:
            fila.lineas.all().delete()
            LineaTicketModel.objects.bulk_create(
                LineaTicketModel(
                    ticket=fila,
                    orden=i,
                    descripcion=li.descripcion,
                    cantidad=li.cantidad,
                    precio_unitario=li.precio_unitario,
                )
                for i, li in enumerate(ticket.lineas, start=1)
            )

    def guardar_texto(self, ticket_id: int, texto: str) -> None:
        TicketModel.objects.filter(pk=ticket_id).update(texto_ocr=texto)

    def terminar_sin_gasto(self, ticket_id: int, estado: EstadoTicket, mensaje: str, ahora) -> bool:
        return bool(
            TicketModel.objects.filter(pk=ticket_id, estado__in=SIN_TERMINAR).update(
                estado=estado, error=mensaje, procesado_en=ahora
            )
        )

    def leer_archivo(self, ticket: Ticket) -> bytes:
        with TicketModel.objects.get(pk=ticket.id).archivo.open("rb") as f:
            return f.read()

    def eliminar(self, ticket: Ticket) -> None:
        TicketModel.objects.filter(pk=ticket.id).delete()
